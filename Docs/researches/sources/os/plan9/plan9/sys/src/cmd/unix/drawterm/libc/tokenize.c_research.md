# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/tokenize.c

This file tokenizes strings with Plan 9 shell-like quote handling.

Key behavior:
- `tokenize` splits on whitespace.
- `gettokens` splits on a caller-provided separator set.
- `qtoken` and `etoken` handle quoted strings and doubled quotes.

Important details:
- Tokenization is in-place and NUL-terminates fields.
- Used by auth attribute parsing and command-style inputs.
