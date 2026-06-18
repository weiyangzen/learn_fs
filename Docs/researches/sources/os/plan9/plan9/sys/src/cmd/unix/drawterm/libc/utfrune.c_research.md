# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfrune.c

This file searches a UTF-8 string for the first occurrence of a rune.

Key behavior:
- `utfrune` returns a pointer to the first matching encoded rune or `nil`.

Important details:
- Handles ASCII fast paths and multibyte decoding.
