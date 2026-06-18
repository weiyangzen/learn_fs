# File Research: sources/teaching/os161/kern/include/endian.h

Kernel-facing endian conversion header.

Key contents:
- Includes exported endian definitions from `<kern/endian.h>`.
- Declares byte-swap functions for 16/32/64-bit values.
- Declares network/host conversion helpers for 16/32/64-bit values.
- Declares `join32to64` and `split64to32`.

Relevance:
- Filesystem on-disk formats in this subset are native/simple, but block and binary-format code can use these conversions.
