# File Research: sources/os/plan9/plan9/sys/src/9/port/unthwack.c

## Role

Implements the `thwack` decompressor and decoder history management.

## Main Data

Static decode tables map compact bit prefixes to literal/match lengths and offset classes. `Unthwack` keeps a circular, sequence-ordered block history. `unthwackstate` reports the newest decoded sequence and a mask of nearby available prior sequences so the encoder can reference shared history.

## Control Flow

`unthwackinit` clears state and assigns each block its backing buffer. `unthwackinsert` inserts a decoded block by sequence, moving block metadata while preserving backing buffers, then advances the circular slot.

`unthwack` validates compressed size, builds a temporary list of the current output block plus referenced history blocks from the compressed header sequence delta/mask, decodes literals and match references from the bitstream, bounds-checks output and history offsets, copies reconstructed bytes to `dst`, then inserts the new block into decoder history.

## Dependencies

Uses `thwack.h` constants and Plan 9 memory/print routines.

## Risks

Malformed streams return negative errors; one missing-history path prints to console. Decompression is sensitive to bit accounting (`utnbits`, `overbits`) and uses overlapping copy semantics manually. Destination size and sequence continuity are caller-visible correctness requirements.
