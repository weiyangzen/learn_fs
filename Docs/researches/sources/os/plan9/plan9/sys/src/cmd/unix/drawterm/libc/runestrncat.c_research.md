# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrncat.c

This file appends a bounded number of runes.

Key behavior:
- `runestrncat` appends up to `n` runes from `s2` to `s1` and terminates.

Important details:
- Caller must provide sufficient destination space.
