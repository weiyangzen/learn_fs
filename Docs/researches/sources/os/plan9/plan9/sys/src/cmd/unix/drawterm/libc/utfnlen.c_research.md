# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfnlen.c

This file counts runes in a bounded UTF-8 byte range.

Key behavior:
- `utfnlen` counts complete runes within at most `m` bytes.

Important details:
- Stops before incomplete trailing UTF sequences.
