# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/conv.c

This file serializes and deserializes flashfs journal records.

Key behavior:
- Converts `Jrec` structures to compact on-flash byte records with `convJ2M`.
- Converts byte records back to normalized `Jrec` structures with `convM2J`.
- Encodes creates, chmods, removes, writes, append-style writes, truncates, and summary markers.
- Uses compact one-, two-, or three-byte integer encoding through `putc3`/`getc3`.
- Provides `%J` formatting for debugging journal records.

Important details:
- Public logical operations such as `FT_create`, `FT_chmod`, and `FT_trunc` are lowered to smaller mode-specific record variants.
- Write sizes are stored as `size - 1`.
- Names are capped by `MAXNSIZE`.

Filesystem relevance:
- Direct: defines flashfs's persistent journal record wire format.
