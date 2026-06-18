# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inftrees.c

## Purpose
Builds canonical Huffman decode tables for inflate.

## Key Elements
Exports `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)`. It counts code lengths, validates over-subscribed/incomplete trees, sorts symbols by length, and fills root/sub-table decode entries. It contains base/extra tables for length and distance symbols.

## Behavior/Risks
Returns `0` on success, `-1` for invalid code lengths, and `+1` when the provided table space is insufficient. It assumes caller-provided lengths are in `0..MAXBITS`; that is not checked internally. For no-symbol cases it creates invalid-code table entries and lets decoding report the error. `ENOUGH` is considered conservatively safe but not exhaustively proven in comments.

## Dependencies
Includes `zutil.h` and `inftrees.h`. Used by `inflate.c` and `infback.c` for fixed and dynamic block table construction.
