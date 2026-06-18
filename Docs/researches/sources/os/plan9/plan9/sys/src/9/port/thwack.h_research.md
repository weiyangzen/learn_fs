# File Research: sources/os/plan9/plan9/sys/src/9/port/thwack.h

## Role

Defines the shared state and public interface for Plan 9's `thwack` block compressor and `unthwack` decompressor. It is a header-only contract used by the encoder and decoder.

## Main Definitions

The constants define the wire and window limits: `ThwMaxBlock` is 1600 bytes, encoder history has `EWinBlocks` 22 blocks, decoder history has `DWinBlocks` 32 blocks, and up to `CompBlocks` 10 blocks may be referenced when decoding one compressed block. Hashing uses a 4096-entry table, with `MinMatch` 3 and sequence acknowledgement mask limits.

`Thwack` owns encoder blocks, per-block hash tables, and backing block data. `Unthwack` owns decoder history blocks and backing data.

## Interfaces

Exports initialization, compression, acknowledgement, decompression, and decoder-state reporting:

- `thwackinit`, `unthwackinit`
- `thwack`, `thwackack`
- `unthwack`, `unthwackstate`

## Risks

All sizing assumptions are compile-time fixed. Callers must respect `ThwMaxBlock`, sequence ordering, and destination buffer sizes; the header does not encode ownership or bounds beyond these constants.
