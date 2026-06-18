# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.h

## Purpose
Internal header for inflate Huffman decode table construction and representation.

## Key Types
Defines `code`:
- `op`: operation, extra-bit count, table-link bit count, end marker, or invalid marker.
- `bits`: number of bits consumed by this table entry.
- `val`: literal byte, base length/distance, or sub-table offset.

Defines `codetype`:
- `CODES`
- `LENS`
- `DISTS`

## Constants
- `ENOUGH 1440`: decode table capacity for dynamic trees.
- `MAXD 154`: maximum distance-table reserve used in capacity checks.

## API
Declares `inflate_table()`, used by inflate implementations to build decode tables from code lengths.

## Notes
The file documents the exact `op` encoding, which is central to `inflate.c`, `infback.c`, and `inffast.c`.
