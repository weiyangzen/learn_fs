# File Research: sources/os/plan9/9front/sys/src/cmd/git/revert

Restores paths from a commit, defaulting to `HEAD`. It resolves the commit path under `git/fs`, normalizes requested file paths relative to the repo, then uses `git/walk -c -fRM -b <query>` to find removed/modified files to restore.

For each path it creates parent directories, copies from the commit tree, updates mtime with `touch -c`, and runs `git/add`.
