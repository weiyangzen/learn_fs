# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrrchr.c

This file searches a rune string backward.

Key behavior:
- `runestrrchr` returns the last occurrence of a rune or `nil`.

Important details:
- Scans forward while remembering the latest match.
