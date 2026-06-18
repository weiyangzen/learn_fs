# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sfxboth.c

Combines both file stream implementations into one translation unit.

Key points:
- Includes `sfxstdio.c` first to provide the normal `FILE *` stream implementation.
- Defines `KEEP_FILENO_API` before including `sfxfd.c`.
- With `KEEP_FILENO_API`, the direct file-descriptor implementation exports alternate names `sread_fileno`, `swrite_fileno`, and `sappend_fileno` instead of colliding with `sread_file`, `swrite_file`, and `sappend_file`.

Research relevance:
- This is a build-composition shim that allows both stdio and direct-OS-call file stream backends to coexist in the same executable.
