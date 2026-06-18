# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcat.c

This file concatenates rune strings.

Key behavior:
- `runestrcat` appends `s2` to the end of `s1`.

Important details:
- Caller must provide sufficient destination space.
