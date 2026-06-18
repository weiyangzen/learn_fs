# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrchr.c

This file searches a rune string forward.

Key behavior:
- `runestrchr` returns the first occurrence of a rune or `nil`.

Important details:
- Can find NUL terminator when searching for zero.
