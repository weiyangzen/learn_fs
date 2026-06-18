# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrlen.c

This file measures rune strings.

Key behavior:
- `runestrlen` counts runes before the NUL terminator.

Important details:
- Rune counterpart to `strlen`.
