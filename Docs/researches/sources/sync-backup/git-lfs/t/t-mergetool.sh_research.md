# sources/sync-backup/git-lfs/t/t-mergetool.sh

## Purpose

Ensures `git mergetool` receives smudged large-file contents for BASE, LOCAL, and REMOTE during an LFS-tracked conflict instead of pointer text.

## Important APIs, control flow, and dependencies

The test creates an LFS-tracked `conflict.dat`, makes conflicting `main` and `conflict` branch commits, runs a merge to produce a conflict, configures a custom mergetool `inspect` command that prints `$BASE`, `$LOCAL`, and `$REMOTE` file contents, and invokes `yes | git mergetool --no-prompt --tool=inspect -- conflict.dat`.

## State, dependencies, integration points, risks, and test signals

State includes conflicted index stages, LFS local object cache, mergetool temp files, and Git mergetool config. Integration points are Git conflict stage materialization, LFS smudge for mergetool files, and mergetool command environment. Risks include passing pointer files to tools, missing base content, or hanging on prompts. Signals are greps for `$BASE=base`, `$LOCAL=a`, and `$REMOTE=b`.
