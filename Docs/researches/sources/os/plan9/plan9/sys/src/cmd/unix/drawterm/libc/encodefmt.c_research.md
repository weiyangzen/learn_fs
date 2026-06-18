# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/encodefmt.c

This file implements encoded byte formatting.

Key behavior:
- `encodefmt` formats byte arrays in encodings selected by the format verb/flags, including hex and base encodings.

Important details:
- Used by Plan 9 `%.*H`/encoding-style formatting conventions.
