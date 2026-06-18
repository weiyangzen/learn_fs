# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_decompress.c

## Purpose

Finite State Entropy decoder implementation, including DTable allocation/building, raw/RLE decode tables, and workspace decompression.

## Main Components

- Allocation:
  - `FSE_createDTable`
  - `FSE_freeDTable`
- Table construction:
  - `FSE_buildDTable`
  - `FSE_buildDTable_rle`
  - `FSE_buildDTable_raw`
- Decompression:
  - `FSE_decompress_usingDTable_generic`
  - `FSE_decompress_usingDTable`
  - `FSE_decompress_wksp`
  - `FSE_decompress`

## ReactOS Adaptation

- Includes `<ntifs.h>` and `<ntddk.h>`.
- `FSE_createDTable` allocates from `PagedPool` with tag `FSED_ALLOC_TAG`.
- `FSE_freeDTable` uses `ExFreePool`.

## Behavior

- `FSE_buildDTable` lays low-probability symbols at the high threshold, spreads remaining symbols, and computes `newState`/`nbBits`.
- `fastMode` is disabled if any normalized count is at least half the table size.
- Decoder initializes two FSE states and emits up to four symbols per loop.
- `FSE_decompress_wksp` reads normalized counts, validates table log against caller maximum, builds the DTable, then decodes the payload.

## Research Notes

- `FSE_decompress()` handles only normal FSE blocks; raw and RLE must be handled by callers.
- Corruption detection depends on table spread reaching every cell and bitstream completion.
- Fast symbol decoding is selected from the DTable header’s `fastMode`.
