#!/usr/bin/env python3
"""Check that a translation changed only the text of its source.

    check_structure.py SOURCE DRAFT [--final]

Works on .docx, .html, .md, and .txt (both files in the same format).
Prints one line per structural mismatch and one line per number that appears
in only one file. Exit code 1 means a structural mismatch; number differences
are for a human to judge, because written number formats change (1,200 -> 1.200).
Use --final to also require matching DOCX segment IDs and no unresolved [?] markers.
"""
import argparse
import collections
from functools import lru_cache
import importlib.util
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
NUMBER = re.compile(r'\d(?:[\d.,  \']*\d)?')    # no plain space: it glued neighbouring numbers together


@lru_cache(maxsize=1)
def load_docx_text():
    spec = importlib.util.spec_from_file_location('docx_text', os.path.join(HERE, 'docx_text.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def numbers(text):
    """Digit sequences with grouping and decimal separators removed."""
    out = collections.Counter()
    for m in NUMBER.findall(text):
        digits = re.sub(r'\D', '', m)
        if digits:
            out[digits] += 1
    return out


# ---------------------------------------------------------------- docx

def describe(i):
    """What an item is, without its words, so moving words around does not count as a change."""
    if i.kind != 'opaque':
        return (str(i.chain), re.sub(r'<w:lang\b[^>]*/>', '', i.rpr), i.kind)   # the language setting is meant to change
    if re.search(r'<w:p[ >]', i.raw):                      # holds a text box: its paragraphs are checked on their own
        return (str(i.chain), 'opaque', 'text box')
    raw = plain(i.raw)
    return (str(i.chain), 'opaque', raw)


def plain(xml):
    """Drop what may change on purpose: the language setting and image descriptions."""
    return re.sub(r'<w:lang\b[^>]*/>', '', load_docx_text().ALT_TEXT.sub('', xml))


def docx_signature(dt, path):
    """Per paragraph id: its formatting items, markers, and frame; per part: the skeleton without paragraph contents."""
    sig, text, skeleton = {}, [], {}
    with zipfile.ZipFile(path) as zf:
        for name in dt.parts_of(zf):
            root, paras, alts, base = dt.read_part(zf, name)
            for P in paras:
                markers = [dt.ser(m) for i in P.model.items for m in i.before] + [dt.ser(m) for m in P.model.tail]
                frame = plain(P.node.open + ''.join(dt.ser(k) for k in P.model.ppr))     # paragraph properties
                sig[P.id] = (P.fallback, sorted(describe(i) for i in P.model.items), sorted(markers), frame)
                if P.text:
                    text.append(dt.decode(re.sub(r'<[^>]*>', '', P.text)))
            for a in alts:
                text.append(dt.decode(dt.ALT_TEXT.search(a.open).group(2)))
            for P in paras:                      # tables, cell merges, sections: everything around the paragraphs
                P.node.kids = P.model.ppr
            skeleton[name] = plain(dt.ser(root))
    return sig, ' '.join(text), skeleton


def check_docx(src, draft):
    dt = load_docx_text()
    problems = []
    with zipfile.ZipFile(src) as a, zipfile.ZipFile(draft) as b:
        if a.namelist() != b.namelist():
            problems.append('file parts differ: %s' % sorted(set(a.namelist()) ^ set(b.namelist())))
        for n in a.namelist():
            if n in b.namelist() and not dt.PARTS.match(n) and n != 'word/styles.xml' and a.read(n) != b.read(n):
                problems.append('part changed that holds no text: ' + n)
        styles = [re.sub(r'<w:lang\b[^>]*/>', '', z.read('word/styles.xml').decode('utf-8'))
                  if 'word/styles.xml' in z.namelist() else '' for z in (a, b)]
        if styles[0] != styles[1]:
            problems.append('styles.xml changed beyond the language setting')
    s1, t1, k1 = docx_signature(dt, src)
    s2, t2, k2 = docx_signature(dt, draft)
    if set(s1) != set(s2):
        problems.append('paragraphs added or removed: %s' % sorted(set(s1) ^ set(s2))[:5])
    for k in s1:
        if k in s2 and not s1[k][0]:
            if s1[k][1] != s2[k][1]:
                problems.append('%s: formatting, tabs, breaks, or non-text items differ' % k)
            if s1[k][2] != s2[k][2]:
                problems.append('%s: bookmarks or comment anchors differ' % k)
            if s1[k][3] != s2[k][3]:
                problems.append('%s: paragraph style or properties differ' % k)
    for name in k1:
        if name in k2 and k1[name] != k2[name]:
            problems.append('%s: tables, cell merges, or sections differ around the paragraphs' % name)
    return problems, numbers(t1), numbers(t2)


# ---------------------------------------------------------------- text formats

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def skeleton_text(text):
    """Keep line structure and markdown syntax, drop the words."""
    out = []
    for line in text.split('\n'):
        m = re.match(r'^(\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+|>\s*)*)', line)
        lead = re.sub(r'\d+', '1', m.group(1))
        rest = line[m.end():]
        if '|' in rest:                                   # table row: keep the cell count and separators
            cells = rest.split('|')
            rest = '|'.join('-' if re.fullmatch(r'\s*:?-{2,}:?\s*', c) else 'x' if c.strip() else '' for c in cells)
        else:
            rest = 'x' if rest.strip() else ''
        out.append(lead + rest)
    return out


def skeleton_html(text):
    tags = re.findall(r'<[^>]+>', text)
    out = []
    for t in tags:
        t = re.sub(r'\s+(alt|title|lang|content)="[^"]*"', '', t)
        out.append(re.sub(r'\s+', ' ', t.lower()))
    return out


def check_text(src, draft):
    a, b = read(src), read(draft)
    ext = os.path.splitext(src)[1].lower()
    sa, sb = (skeleton_html(a), skeleton_html(b)) if ext in ('.html', '.htm') else (skeleton_text(a), skeleton_text(b))
    problems = []
    if len(sa) != len(sb):
        problems.append('%d lines or tags in the source, %d in the draft' % (len(sa), len(sb)))
    for i, (x, y) in enumerate(zip(sa, sb), 1):
        if x != y:
            problems.append('item %d: source %r, draft %r' % (i, x[:60], y[:60]))
            if len(problems) > 20:
                break
    if ext in ('.html', '.htm'):
        a, b = re.sub(r'<[^>]+>', ' ', a), re.sub(r'<[^>]+>', ' ', b)
    return problems, numbers(a), numbers(b)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('draft')
    parser.add_argument('--final', action='store_true')
    args = parser.parse_args()
    src, draft = args.source, args.draft
    ext = os.path.splitext(src)[1].lower()
    if ext != os.path.splitext(draft)[1].lower():
        sys.exit('source and draft need the same format')
    if ext == '.docx':
        problems, n1, n2 = check_docx(src, draft)
        dt = load_docx_text()
        source_segments = {s['id'] for s in dt.extract(src)['segments']}
        draft_segments = {s['id']: s['text'] for s in dt.extract(draft)['segments']}
        print('DOCX segments: %d source, %d draft' % (len(source_segments), len(draft_segments)))
        if args.final and source_segments != draft_segments.keys():
            problems.append('translatable segment IDs differ: %s' % sorted(source_segments ^ draft_segments.keys()))
        markers = [sid for sid, value in draft_segments.items()
                   if '[?]' in dt.decode(re.sub(r'<[^>]*>', '', value))] if args.final else []
    elif ext in ('.html', '.htm', '.md', '.txt'):
        problems, n1, n2 = check_text(src, draft)
        markers = ['line %d' % i for i, line in enumerate(read(draft).splitlines(), 1)
                   if '[?]' in line] if args.final else []
    else:
        sys.exit('unsupported format: ' + ext)
    for p in problems:
        print('STRUCTURE', p)
    for location in markers:
        print('UNRESOLVED [?]:', location)
    for d, only in (('source', n1 - n2), ('draft', n2 - n1)):
        for num, k in sorted(only.items()):
            print('NUMBER only in %s: %s (x%d)' % (d, num, k))
    print('structure: %s; numbers: %s' % ('MISMATCH' if problems else 'ok',
                                          'differences listed' if (n1 - n2) or (n2 - n1) else 'ok'))
    sys.exit(1 if problems or markers else 0)


if __name__ == '__main__':
    main()
