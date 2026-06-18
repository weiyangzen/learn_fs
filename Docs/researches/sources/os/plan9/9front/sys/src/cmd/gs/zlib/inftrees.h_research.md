# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.h

## Purpose
Defines internal Huffman decode table types for inflate.

## Key Elements
Defines `code` with `op`, `bits`, and `val` fields; `ENOUGH` and `MAXD`; `codetype` values `CODES`, `LENS`, and `DISTS`; and the `inflate_table` prototype.

## Behavior/Risks
The `op` encoding distinguishes literals, sub-table links, length/distance extra bits, end-of-block, and invalid-code entries. The header is private to zlib internals and tightly coupled to table generation and fast decode logic.

## Dependencies
Depends on zlib portability macros such as `FAR` and `OF`.
