# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcpy.c

This file copies rune strings.

Key behavior:
- `runestrcpy` copies `s2` including NUL into `s1`.

Important details:
- Caller must provide enough destination space.
