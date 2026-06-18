# File Research: sources/os/plan9/9front/sys/src/cmd/echo.c

This is a compact Plan 9 `echo` implementation.

Key responsibilities:
- Supports a single `-n` option to suppress the trailing newline.
- Computes the exact output buffer length, allocates it, concatenates arguments separated by spaces, and optionally appends `\n`.
- Writes the buffer to stdout with one `write`.

Important implementation notes:
- The parser only recognizes `-n` as the first argument; all other arguments are printed literally.
- On allocation failure it exits with `"no memory"`.
- On write failure it reports `echo: write error: %r` to stderr and exits with `"write error"`.
