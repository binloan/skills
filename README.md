# binloan-masterskill

TODO: Explain what someone can accomplish with this skill in one sentence.

## Install

From the project where you want to use the skill, run the following command with Node.js 22.20 or later. Replace `YOUR_GITHUB_OWNER` with the GitHub user or organization that owns the public repository.

```sh
npx skills add YOUR_GITHUB_OWNER/binloan-masterskill --skill binloan-masterskill
```

## Try it

TODO: Give one prompt a user can paste into their agent after installation.

## Finish and publish the template

1. Fill in the description, inputs, workflow, and example in [SKILL.md](skills/binloan-masterskill/SKILL.md). The description helps agents decide when to use the skill.
2. Replace the `TODO` fields and `YOUR_GITHUB_OWNER` in this README. If you choose a license, add its text in a root `LICENSE` file.
3. From the repository root, run `npx skills add . --list`. The output should include `binloan-masterskill`.
4. Create an empty public GitHub repository named `binloan-masterskill`. From this directory, publish your completed files with the commands below.

```sh
git add .
git commit -m "Add binloan-masterskill"
git remote add origin https://github.com/YOUR_GITHUB_OWNER/binloan-masterskill.git
git push -u origin main
```

After the push, run the install command from a separate project and try the example prompt. See the [official skills CLI guide](https://github.com/vercel-labs/skills).
