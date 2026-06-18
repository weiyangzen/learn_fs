# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrrune.c

This file searches a UTF-8 string for the last occurrence of a rune.

Key behavior:
- `utfrrune` scans decoded runes and remembers the most recent match.

Important details:
- Handles ASCII fast paths and multibyte decoding.
