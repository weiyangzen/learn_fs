# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrdup.c

This file duplicates rune strings.

Key behavior:
- `runestrdup` allocates and copies a NUL-terminated rune string.

Important details:
- Returns `nil` on allocation failure.
