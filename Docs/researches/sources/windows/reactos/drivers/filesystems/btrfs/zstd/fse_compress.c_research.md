# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_compress.c

## Purpose

Finite State Entropy encoder implementation, including CTable construction, normalized-count serialization, count normalization, raw/RLE table construction, and one-shot/workspace compression.

## Main Components

- Table construction:
  - `FSE_buildCTable_wksp`
  - `FSE_buildCTable`
  - `FSE_buildCTable_raw`
  - `FSE_buildCTable_rle`
- Normalized-count writing:
  - `FSE_NCountWriteBound`
  - `FSE_writeNCount_generic`
  - `FSE_writeNCount`
- Allocation:
  - `FSE_createCTable`
  - `FSE_freeCTable`
- Table-log selection:
  - `FSE_minTableLog`
  - `FSE_optimalTableLog_internal`
  - `FSE_optimalTableLog`
- Count normalization:
  - `FSE_normalizeM2`
  - `FSE_normalizeCount`
- Compression:
  - `FSE_compress_usingCTable_generic`
  - `FSE_compress_usingCTable`
  - `FSE_compressBound`
  - `FSE_compress_wksp`
  - `FSE_compress2`
  - `FSE_compress`

## ReactOS Adaptation

- Includes `<ntifs.h>` and `<ntddk.h>`.
- `FSE_createCTable` allocates from `PagedPool` with tag `FSEC_ALLOC_TAG`.
- `FSE_freeCTable` uses `ExFreePool`.

## Behavior

- Builds a symbol spread table using `FSE_TABLESTEP`.
- Encodes low-probability symbols with normalized count `-1`.
- Writes FSE normalized counts into compact bit-packed headers.
- Counts input symbols through `HIST_count_wksp`.
- Rejects inputs that are too small, likely incompressible, or not worth storing compressed.
- Encodes streams backward with two FSE states and `BIT_CStream_t`.

## Research Notes

- Workspace alignment and sizing are critical; the function reuses the caller’s workspace for both CTable and scratch table symbols.
- `FSE_normalizeCount` has a primary fast normalization path and a secondary `FSE_normalizeM2` fallback for difficult rounding cases.
- Return value `0` means not compressible or not storable; return value `1` means RLE in the high-level compression path.
