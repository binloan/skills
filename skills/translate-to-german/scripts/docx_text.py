#!/usr/bin/env python3
"""Extract and inject the text of a .docx so a translation changes nothing else.

    docx_text.py extract SOURCE.docx [-o segments.json]
    docx_text.py inject  SOURCE.docx translation.json OUT.docx [--lang de-DE]

extract writes one segment per paragraph (and per image alt text) with an ID,
a location label, and the text. Write the translation as a JSON map of
{"id": "translated text"} with the same IDs and run inject. Every part of the
file that holds no translated text or language settings is copied byte for byte.

Markup inside segment text (angle brackets and & are written as &lt; &gt; &amp;):
    <t1>..</t1>   text with one formatting. Used only when a paragraph has
                  more than one. Keep every tag, and move tags with the words.
    <o1/>         a non-text item (image, footnote mark, field, ...). Keep each once.
    <tab/> <br/>  a tab or a line break. Keep the same number.
"""
import argparse
import json
import re
import sys
import zipfile

sys.setrecursionlimit(20000)

TOKEN = re.compile(
    r'<!--.*?-->|<\?.*?\?>|<!\[CDATA\[.*?\]\]>|<(?:[^>"\']|"[^"]*"|\'[^\']*\')*>|[^<]+', re.S)
PARTS = re.compile(r'word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$')
CONTAINERS = {'w:hyperlink', 'w:ins', 'w:smartTag', 'w:customXml'}
MARKERS = {'w:bookmarkStart', 'w:bookmarkEnd', 'w:commentRangeStart', 'w:commentRangeEnd',
           'w:permStart', 'w:permEnd', 'w:proofErr', 'w:del', 'w:moveFromRangeStart',
           'w:moveFromRangeEnd', 'w:moveToRangeStart', 'w:moveToRangeEnd'}
ENTITY = re.compile(r'&(#x[0-9A-Fa-f]+|#[0-9]+|lt|gt|amp|quot|apos);')
NAMED = {'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': "'"}
TR = re.compile(r'<t(\d+)>|</t(\d+)>|<o(\d+)/>|<tab/>|<br/>|[^<]+|<[^>]*>')
ALT_TEXT = re.compile(r'''(?<=\s)descr=(["'])(.*?)\1''', re.S)


# ---------------------------------------------------------------- XML tree

class Node:
    """Element (name set) or raw leaf (name None). Raw strings keep the file byte-exact."""
    __slots__ = ('name', 'open', 'close', 'kids')

    def __init__(self, name, open_, close=''):
        self.name, self.open, self.close, self.kids = name, open_, close, []

    def text(self):
        return decode(''.join(k.open for k in self.kids if k.name is None))


def parse(xml):
    root = Node('#root', '')
    stack = [root]
    for m in TOKEN.finditer(xml):
        raw = m.group()
        if raw[0] != '<' or raw.startswith(('<!--', '<?', '<![CDATA[')):
            stack[-1].kids.append(Node(None, raw))
        elif raw.startswith('</'):
            stack.pop().close = raw
        else:
            node = Node(re.match(r'<([^\s/>]+)', raw).group(1), raw)
            stack[-1].kids.append(node)
            if not raw.endswith('/>'):
                stack.append(node)
    if len(stack) != 1 or ser(root) != xml:
        raise ValueError('XML part does not round-trip')
    return root


def ser(n):
    return n.open if n.name is None else n.open + ''.join(map(ser, n.kids)) + n.close


def iter_nodes(n):
    yield n
    for k in n.kids:
        yield from iter_nodes(k)


def own_text(n):
    """Text of n, leaving out text boxes (their paragraphs are segments of their own)."""
    if n.name in ('w:t', 'w:delText'):
        return n.text()
    if n.name in ('w:txbxContent', 'mc:Fallback'):
        return ''
    return ''.join(own_text(k) for k in n.kids)


def decode(s):
    def one(m):
        e = m.group(1)
        if e[0] != '#':
            return NAMED[e]
        return chr(int(e[2:], 16) if e[1] == 'x' else int(e[1:]))
    return ENTITY.sub(one, s)


def enc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def encode_attribute(text):
    return (enc(text).replace('"', '&quot;').replace("'", '&apos;')
            .replace('\t', '&#9;').replace('\n', '&#10;').replace('\r', '&#13;'))


# ---------------------------------------------------------------- paragraph model

class Item:
    __slots__ = ('kind', 'chain', 'rpr', 'text', 'raw', 'num', 'occ', 'before')

    def __init__(self, kind, chain, rpr='', text='', raw=''):
        self.kind, self.chain, self.rpr, self.text, self.raw = kind, chain, rpr, text, raw
        self.num = self.occ = 0
        self.before = []     # marker elements (bookmarks, ...) that precede this item

    @property
    def key(self):
        return ('s' if self.kind == 'text' else self.kind, self.num)


def wrap(chain, xml):
    return ''.join(p for p, _ in chain) + xml + ''.join(s for _, s in reversed(chain))


class Model:
    """A paragraph as text items, with the raw pieces needed to rebuild it."""

    def __init__(self, p, depth):
        self.ppr = [k for k in p.kids if k.name == 'w:pPr']
        self.items, self.pending = [], []
        self.slots = {}          # (chain, rpr) -> index
        self.fields = []         # visible text kept inside fields
        self.depth = depth       # open complex fields
        self.group = None        # open field group
        self.scan(p.kids, ())
        self.tail = self.pending
        self.number()

    def add(self, item):
        item.before, self.pending = self.pending, []
        self.items.append(item)

    def scan(self, kids, chain):
        for k in kids:
            nm = k.name
            if nm is None or nm == 'w:pPr':
                continue
            if nm == 'w:r':
                self.run(k, chain)
            elif nm in CONTAINERS:
                self.scan(k.kids, chain + ((k.open, k.close),))
            elif nm == 'w:sdt':
                content = next((c for c in k.kids if c.name == 'w:sdtContent'), None)
                if content is None:
                    self.opaque(k, chain)
                    continue
                i = k.kids.index(content)
                prefix = k.open + ''.join(map(ser, k.kids[:i])) + content.open
                suffix = content.close + ''.join(map(ser, k.kids[i + 1:])) + k.close
                self.scan(content.kids, chain + ((prefix, suffix),))
            elif nm in MARKERS:
                self.pending.append(k)
            else:
                self.opaque(k, chain)       # fldSimple, math, alternate content, ...

    def opaque(self, node, chain, in_field=False):
        if in_field and self.group is not None:
            self.group.raw += ser(node)
        else:
            it = Item('opaque', chain, raw=ser(node))
            self.add(it)
            self.group = it if in_field else None
        txt = own_text(node)
        if any(c.isalpha() for c in txt):
            self.fields.append(txt)

    def run(self, r, chain):
        kids = [k for k in r.kids if k.name not in (None, 'w:rPr')]
        rpr = ''.join(ser(k) for k in r.kids if k.name == 'w:rPr')
        fld = [k for k in kids if k.name == 'w:fldChar']
        if fld:
            m = re.search(r'w:fldCharType="(\w+)"', fld[0].open)
            typ = m.group(1) if m else ''
            if typ == 'begin':
                self.depth += 1
            self.opaque(r, chain, in_field=True)
            if typ == 'end':
                self.depth = max(0, self.depth - 1)
                if self.depth == 0:
                    self.group = None
            return
        if self.depth > 0:
            self.opaque(r, chain, in_field=True)
            return
        self.group = None
        if not all(k.name in ('w:t', 'w:tab', 'w:lastRenderedPageBreak')
                   or (k.name == 'w:br' and re.fullmatch(r'<w:br\s*/>', k.open)) for k in kids):
            self.opaque(r, chain)
            return
        for k in kids:
            if k.name == 'w:t' and k.text():
                self.add(Item('text', chain, rpr, text=k.text()))
            elif k.name in ('w:tab', 'w:br'):
                self.add(Item(k.name[2:], chain, rpr))

    def number(self):
        n, merged, seen = {'tab': 0, 'br': 0, 'opaque': 0}, [], {}
        for it in self.items:
            if it.kind == 'text':
                it.num = self.slots.setdefault((it.chain, it.rpr), len(self.slots) + 1)
                prev = merged[-1] if merged else None
                if prev is not None and prev.kind == 'text' and prev.num == it.num:
                    prev.text += it.text
                    prev.before += it.before
                    continue
            else:
                n[it.kind] += 1
                it.num = n[it.kind]
            seen[it.key] = it.occ = seen.get(it.key, 0) + 1
            merged.append(it)
        self.items, self.counts = merged, n

    def text(self):
        if not self.slots:
            return None
        tagged = len(self.slots) > 1
        out, cur = [], None
        for it in self.items:
            if it.kind == 'text':
                if tagged and cur != it.num:
                    if cur:
                        out.append('</t%d>' % cur)
                    out.append('<t%d>' % it.num)
                    cur = it.num
                out.append(enc(it.text))
            else:
                if cur:
                    out.append('</t%d>' % cur)
                    cur = None
                out.append({'tab': '<tab/>', 'br': '<br/>'}.get(it.kind) or '<o%d/>' % it.num)
        if cur:
            out.append('</t%d>' % cur)
        s = ''.join(out)
        return s if any(c.isalpha() for c in decode(re.sub(r'<[^>]*>', '', s))) else None   # tags first: a literal < is written &lt;


# ---------------------------------------------------------------- locate paragraphs

class Para:
    def __init__(self, node, num, loc, nested, fallback):
        self.node, self.num, self.loc, self.nested, self.fallback = node, num, loc, nested, fallback
        self.id = self.model = self.text = None


def collect(root):
    paras, alts, st = [], [], {'tbl': 0, 'p': 0}

    def walk(n, loc, nested, fallback):
        nm = n.name
        if nm is None or nm == 'w:del':
            return
        if nm == 'mc:Fallback':
            fallback = True
        if nm == 'wp:docPr' and not fallback:
            description = ALT_TEXT.search(n.open)
            if description and decode(description.group(2)).strip():
                alts.append(n)
        if nm == 'w:txbxContent':
            loc = loc + ('text box',)
        if nm == 'w:p':
            st['p'] += 1
            paras.append(Para(n, st['p'], loc, nested, fallback))
            nested = True
        if nm == 'w:tbl':
            st['tbl'] += 1
            t, r = st['tbl'], 0
            for k in n.kids:
                if k.name == 'w:tr':
                    r += 1
                    c = 0
                    for cell in k.kids:
                        if cell.name == 'w:tc':
                            c += 1
                            where = loc + ('table %d' % t, 'row %d' % r, 'col %d' % c)
                            for x in cell.kids:
                                walk(x, where, nested, fallback)
                        else:
                            walk(cell, loc, nested, fallback)
                else:
                    walk(k, loc, nested, fallback)
            return
        for k in n.kids:
            walk(k, loc, nested, fallback)

    walk(root, (), False, False)
    return paras, alts


def label(P):
    parts = list(P.loc)
    ppr = next((k for k in P.node.kids if k.name == 'w:pPr'), None)
    if ppr is not None:
        raw = ser(ppr)
        style = re.search(r'<w:pStyle [^>]*w:val="([^"]*)"', raw)
        if style:
            parts.append(style.group(1))
        if '<w:numPr>' in raw:
            parts.append('list item')
    return ', '.join(parts) or 'body'


def read_part(zf, name):
    root = parse(zf.read(name).decode('utf-8'))
    paras, alts = collect(root)
    depth, base = 0, name[5:-4]
    kind = re.match(r'[a-z]+', base).group()
    for P in paras:
        P.id = '%s:%d' % (base, P.num)
        if kind != 'document':
            P.loc = (kind,) + P.loc
        P.model = Model(P.node, 0 if P.nested else depth)
        if not P.nested:
            depth = P.model.depth
        P.text = None if P.fallback else P.model.text()
    return root, paras, alts, base


def parts_of(zf):
    return sorted(n for n in zf.namelist() if PARTS.match(n))


# ---------------------------------------------------------------- extract

def extract(path):
    segs, warns = [], []
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        for name in parts_of(zf):
            root, paras, alts, base = read_part(zf, name)
            for P in paras:
                if P.fallback:
                    if P.model.text():
                        warns.append('%s: copy inside mc:Fallback left as is (read only by Word 2007 and older)' % P.id)
                    continue
                if P.text is not None:
                    segs.append({'id': P.id, 'loc': label(P), 'text': P.text})
                for f in P.model.fields:
                    warns.append('%s: text inside a field or object left as is: %r' % (P.id, f[:60]))
            for i, a in enumerate(alts, 1):
                text = ALT_TEXT.search(a.open).group(2)
                segs.append({'id': 'alt:%s:%d' % (base, i), 'loc': 'image alt text', 'text': text})
        xml = zf.read('word/document.xml').decode('utf-8')
        info = {'tracked_insertions': xml.count('<w:ins '), 'tracked_deletions': xml.count('<w:del '),
                'comments': len(re.findall(r'<w:comment ', zf.read('word/comments.xml').decode('utf-8')))
                if 'word/comments.xml' in names else 0}
    return {'source': path, 'info': info, 'warnings': warns, 'segments': segs}


# ---------------------------------------------------------------- inject

def build(P, tr):
    """Return the new inner XML of paragraph P for the translated text tr."""
    m, out, errs = P.model, [], []
    tagged = len(m.slots) > 1
    inv = {v: k for k, v in m.slots.items()}
    first, anchors, seen = {}, {}, {}
    for it in m.items:
        first.setdefault(it.key, it)
        anchors[(it.key, it.occ)] = it.before
    used, seen_o, count = set(), set(), {'tab': 0, 'br': 0}
    cur = last = None

    def emit(key, xml):
        # markers keep their place: they go before the same occurrence of the same item
        seen[key] = seen.get(key, 0) + 1
        out.extend(ser(mk) for mk in anchors.pop((key, seen[key]), []))
        out.append(xml)

    def text(slot, s):
        chain, rpr = inv[slot]
        used.add(slot)
        emit(('s', slot), wrap(chain, '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, enc(s))))

    pieces = list(TR.finditer(tr))
    if ''.join(x.group() for x in pieces) != tr:
        errs.append('stray "<" (write it as &lt;)')
    for mt in pieces:
        raw = mt.group()
        if mt.group(1):
            if cur or int(mt.group(1)) not in inv:
                errs.append('bad or nested tag ' + raw)
            cur = last = int(mt.group(1))
        elif mt.group(2):
            if cur != int(mt.group(2)):
                errs.append('unpaired tag ' + raw)
            cur = None
        elif mt.group(3):
            n = int(mt.group(3))
            if ('opaque', n) not in first or n in seen_o:
                errs.append('unknown or repeated ' + raw)
            else:
                seen_o.add(n)
                it = first[('opaque', n)]
                emit(it.key, wrap(it.chain, it.raw))
        elif raw in ('<tab/>', '<br/>'):
            kind = raw[1:-2]
            count[kind] += 1
            it = first.get((kind, count[kind]))
            if it is None:
                errs.append('too many ' + raw)
            else:
                emit(it.key, wrap(it.chain, '<w:r>%s<w:%s/></w:r>' % (it.rpr, kind)))
        elif raw[0] == '<':
            errs.append('unknown tag ' + raw)
        else:
            s = decode(raw)
            if not tagged:
                text(1, s)
            elif cur:
                text(cur, s)
            elif s.strip():
                errs.append('text outside tags: %r' % s[:30])
            elif last:
                text(last, s)
    if cur:
        errs.append('unclosed tag')
    if tagged and used != set(inv):
        errs.append('formatting tags missing: ' + ', '.join('t%d' % i for i in sorted(set(inv) - used)))
    if not tagged and not used:
        errs.append('empty translation')
    if seen_o != set(range(1, m.counts['opaque'] + 1)):
        errs.append('non-text items missing or repeated')
    if (count['tab'], count['br']) != (m.counts['tab'], m.counts['br']):
        errs.append('tab or line-break count changed')
    if errs:
        raise ValueError('%s: %s' % (P.id, '; '.join(errs)))
    out.extend(ser(mk) for rest in anchors.values() for mk in rest)
    out.extend(ser(mk) for mk in m.tail)
    return ''.join(out)


def set_lang(xml, lang):
    return re.subn(r'(<w:lang\b[^>]*\bw:val=")[^"]*(")', lambda m: m.group(1) + lang + m.group(2), xml)


def inject(src, seg_path, out, lang=None, rebuild_all=False):
    with open(seg_path, encoding='utf-8') as f:
        data = json.load(f)
    # either the file written by extract, or a plain {"id": "text"} map
    tr = {s['id']: s['text'] for s in data['segments']} if 'segments' in data else data
    repl, used, errors, changed = {}, set(), [], 0
    with zipfile.ZipFile(src) as zf:
        for name in parts_of(zf):
            root, paras, alts, base = read_part(zf, name)
            for P in reversed(paras):          # inner paragraphs first
                if P.text is None:
                    continue
                used.add(P.id)
                if P.id not in tr:
                    errors.append('%s: segment missing in file' % P.id)
                elif tr[P.id] != P.text or rebuild_all:
                    try:
                        xml = build(P, tr[P.id])
                    except ValueError as e:
                        errors.append(str(e))
                        continue
                    P.node.kids = P.model.ppr + [Node(None, xml)]
                    changed += 1
            for i, a in enumerate(alts, 1):
                sid = 'alt:%s:%d' % (base, i)
                used.add(sid)
                if sid not in tr:
                    errors.append('%s: segment missing in file' % sid)
                    continue
                new = decode(tr[sid])
                if not new.strip():
                    errors.append('%s: image description is empty' % sid)
                    continue
                description = ALT_TEXT.search(a.open)
                if new != decode(description.group(2)):
                    start, end = description.span(2)
                    a.open = a.open[:start] + encode_attribute(new) + a.open[end:]
                    changed += 1
            text = ser(root)
            if lang:
                text, _ = set_lang(text, lang)
            if text != zf.read(name).decode('utf-8'):
                repl[name] = text.encode('utf-8')
        extra = sorted(set(tr) - used)
        if extra:
            errors.append('unknown segment IDs: ' + ', '.join(extra[:10]))
        if errors:
            raise SystemExit('inject failed, nothing written:\n  ' + '\n  '.join(errors))
        if lang and 'word/styles.xml' in zf.namelist():
            sx = zf.read('word/styles.xml').decode('utf-8')
            sx2, n = set_lang(sx, lang)
            if n == 0:
                sx2 = re.sub(r'(<w:rPrDefault>\s*<w:rPr>)(.*?)(</w:rPr>)',
                             lambda m: m.group(1) + m.group(2) + '<w:lang w:val="%s"/>' % lang + m.group(3),
                             sx, count=1, flags=re.S)
            if sx2 != sx:
                repl['word/styles.xml'] = sx2.encode('utf-8')
        with zipfile.ZipFile(out, 'w') as zo:
            for info in zf.infolist():
                zo.writestr(info, repl.get(info.filename, zf.read(info)), compress_type=info.compress_type)
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('extract')
    e.add_argument('source')
    e.add_argument('-o', '--output')
    i = sub.add_parser('inject')
    i.add_argument('source')
    i.add_argument('segments')
    i.add_argument('output')
    i.add_argument('--lang')
    i.add_argument('--rebuild-all', action='store_true', help='rebuild every paragraph (for testing)')
    a = ap.parse_args()
    if a.cmd == 'extract':
        res = extract(a.source)
        text = json.dumps(res, ensure_ascii=False, indent=1)
        if a.output:
            with open(a.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print('%d segments, %d warnings -> %s' % (len(res['segments']), len(res['warnings']), a.output))
        else:
            print(text)
    else:
        print('%d text segments changed -> %s' % (inject(a.source, a.segments, a.output, a.lang, a.rebuild_all), a.output))


if __name__ == '__main__':
    main()
