# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/strtoll.c

This file implements signed long long parsing.

Key behavior:
- `strtoll` handles whitespace, sign, base autodetection, digit conversion, and overflow bounds.

Important details:
- Supports base 0, octal, decimal, and hex prefixes.
- Uses `vlong`/`uvlong` Plan 9 integer types.
