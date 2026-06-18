# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncmp.c

This file compares bounded rune strings.

Key behavior:
- `runestrncmp` compares up to `n` runes from two strings.

Important details:
- Stops at NUL or after `n` runes.
