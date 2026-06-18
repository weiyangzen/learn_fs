# File Research: sources/os/plan9/9front/sys/src/cmd/troff/space.c

Read completely: 74 lines, 1237 bytes.

Small whitespace/word parsing helpers. It provides string-level skipping and fd-level reading of whitespace-delimited words.

Key behavior:
- `skipspace` advances past C `isspace` bytes.
- `skipword` advances past non-space bytes.
- `rdspace` reads and discards whitespace from an fd, returning the first non-space byte or EOF/error.
- `rdword` fills a buffer with a word after leading whitespace, stops at whitespace or buffer limit, and NUL-terminates.

Dependencies:
- Uses Plan 9 `read`, `<ctype.h>`, and libc types.

Reliability notes:
- `rdword` reserves one byte for NUL and stops when the buffer is full, so long words are truncated at the caller-provided maximum.
