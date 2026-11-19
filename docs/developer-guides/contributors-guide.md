<!--
Purpose: Show contributors how to submit documentation changes to this repository.
Audience: This guide is intended for ngGONG project developers who can push to this repository.
Style: Instructional and direct. Use short steps and commands.
-->

# Contributor's Guide

This guide shows new and occasional ngGONG documentation contributors how to submit changes to this repository.
It assumes you can push to `nggong/docs` and already have Git and GitHub CLI (`gh`) installed.
See the [GitHub CLI installation instructions] if needed.

## Clone the repository

If you have an SSH authentication key registered with GitHub, use SSH:

```sh
git clone git@github.com:nggong/docs.git
```

Otherwise, use HTTPS:

```sh
git clone https://github.com/nggong/docs.git
```

## Create a branch

```sh
cd docs
git switch -c describe-your-change
```

## Write and check your changes

Create or edit the documentation on your branch.
Follow the [Author's Guide] for writing guidance and the [preview guide] to check the rendered page.
Run `make check` to check spelling.

## Commit your changes

Set up [Git commit signing] before your first commit.
Replace the example path with each file you changed, review the staged changes, then make a signed commit:

```sh
git add -- path/to/changed-file.md
git diff --staged
git commit -S -m "Describe the change"
```

## Create a pull request

```sh
git push -u origin HEAD
```

Then create the pull request:

```sh
gh pr create --repo nggong/docs --base main --template .github/PULL_REQUEST_TEMPLATE.md
```

Complete the pull request template's **Context**, **Verification**, and **Charge to reviewers** sections.
Use `gh pr checks` to see the automated check results.

[GitHub CLI installation instructions]: https://github.com/cli/cli#installation
[Author's Guide]: authors-guide.md
[preview guide]: docker-preview.md
[Git commit signing]: git-commit-signing.md
