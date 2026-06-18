# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utflen.c

This file counts runes in a UTF-8 string.

Key behavior:
- `utflen` walks a NUL-terminated UTF-8 string and counts decoded runes.

Important details:
- Uses `chartorune` for multibyte sequences.
