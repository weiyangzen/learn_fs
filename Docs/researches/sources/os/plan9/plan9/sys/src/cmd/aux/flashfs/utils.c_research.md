# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/utils.c

This file defines flashfs global state and compact integer helpers.

Key behavior:
- Defines `prog`, sector geometry globals, sector buffer, read-only state, clock delta, generation parity, and magic bytes.
- Encodes unsigned values below 2^21 into one to three bytes with continuation high bits.
- Decodes that compact form.
- Reads and writes little-endian 32-bit values.

Important details:
- `putc3` aborts if the value cannot fit in three bytes.
- The magic bytes are `ROO0`.

Filesystem relevance:
- Direct support for flashfs on-disk format encoding.
