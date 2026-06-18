# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrstr.c

This file searches for a rune substring.

Key behavior:
- `runestrstr` returns the first occurrence of `s2` inside `s1`.

Important details:
- Empty needle matches the start of `s1`.
