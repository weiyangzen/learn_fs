# File Research: sources/os/plan9/9front/sys/src/cmd/cat.c

Purpose: Minimal Plan 9 `cat` implementation.

Key points:
- `cat` copies from an input file descriptor to stdout using an `IOUNIT` stack buffer.
- Reports write or read errors with `sysfatal`.
- With no file arguments, reads stdin.
- With files, opens each read-only, copies, and closes it.

Dependencies and interactions:
- Uses Plan 9 `<u.h>` and `<libc.h>`.
- Standalone command.

Research notes:
- No options are supported.
- Errors are fatal and stop processing immediately.
