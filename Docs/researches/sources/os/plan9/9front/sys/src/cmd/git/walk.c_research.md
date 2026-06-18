# File Research: sources/os/plan9/9front/sys/src/cmd/git/walk.c

Working-tree/index status engine. It compares `.git/INDEX9`, a base tree under `git/fs`, and filesystem entries, producing status classes removed, modified, added, untracked, or tracked/clean. It can be quiet for status-only checks and can filter by path, base commit, output classes, and relative output root.

It maintains/refreshes `.git/INDEX9` when stale, comparing Qids/modes first and falling back to byte comparison against the checked-in tree. It ignores `.git`, handles path prefix matching for directories, supports base trees via `-b`, and exits with a status string containing dirty classes.
