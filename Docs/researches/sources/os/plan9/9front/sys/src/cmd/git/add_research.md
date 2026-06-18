# File Research: sources/os/plan9/9front/sys/src/cmd/git/add

rc script for staging files in 9front git.

Key responsibilities:
- Initializes git environment through `common.rc` and `gitup`.
- Parses `-r` to stage removals instead of additions.
- Cleans input paths relative to the repo root.
- Walks files while excluding `.git`, then appends staging rows to `.git/INDEX9`.

Important behavior:
- Addition rows use `A NOQID 0 path`; removal rows use `R NOQID 0 path`.
- Requires at least one path argument.
