# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfutf.c

This file searches for a UTF-8 substring.

Key behavior:
- `utfutf` finds the first occurrence of `s2` in `s1`.

Important details:
- Uses byte substring search with UTF-aware first-rune positioning.
