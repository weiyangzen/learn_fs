# File Research: sources/os/plan9/9front/sys/src/cmd/mkdir.c

Implements Plan 9 `mkdir` with `-p` and `-m mode`.

Key behavior:
- `makedir()` checks for existing paths and creates directories with `DMDIR | mode`.
- `mkdirp()` walks slash-separated prefixes, creating missing components.
- Parses octal modes up to `0777`.

Important dependencies: Plan 9 `create`, `access`, `DMDIR`.

Notable risks:
- `mkdir -p` silently succeeds for already-existing final paths, while non-`-p` reports existing path as an error.
- `mkdirp()` temporarily writes NULs into the argument string.
