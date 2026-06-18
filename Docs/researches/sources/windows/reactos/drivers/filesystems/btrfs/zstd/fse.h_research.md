# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse.h

## Purpose

Public and static-link API header for Finite State Entropy. It declares high-level FSE compression/decompression, advanced table APIs, workspace variants, and inline symbol encode/decode primitives.

## Main Components

- Public API:
  - `FSE_compress`
  - `FSE_decompress`
  - `FSE_compressBound`
  - `FSE_isError`
  - `FSE_getErrorName`
  - `FSE_compress2`
- Detailed compression APIs:
  - `FSE_optimalTableLog`
  - `FSE_normalizeCount`
  - `FSE_NCountWriteBound`
  - `FSE_writeNCount`
  - `FSE_createCTable`
  - `FSE_freeCTable`
  - `FSE_buildCTable`
  - `FSE_compress_usingCTable`
- Detailed decompression APIs:
  - `FSE_readNCount`
  - `FSE_createDTable`
  - `FSE_freeDTable`
  - `FSE_buildDTable`
  - `FSE_decompress_usingDTable`
- Static-link-only sizing and workspace macros:
  - `FSE_NCOUNTBOUND`
  - `FSE_BLOCKBOUND`
  - `FSE_COMPRESSBOUND`
  - `FSE_CTABLE_SIZE_U32`
  - `FSE_DTABLE_SIZE_U32`
  - `FSE_WKSP_SIZE_U32`
- Inline state APIs:
  - `FSE_CState_t`
  - `FSE_DState_t`
  - `FSE_initCState`
  - `FSE_initCState2`
  - `FSE_encodeSymbol`
  - `FSE_flushCState`
  - `FSE_initDState`
  - `FSE_decodeSymbol`
  - `FSE_decodeSymbolFast`
  - `FSE_endOfDState`
- Constants:
  - `FSE_MAX_TABLELOG`
  - `FSE_DEFAULT_TABLELOG`
  - `FSE_MIN_TABLELOG`
  - `FSE_TABLELOG_ABSOLUTE_MAX`
  - `FSE_TABLESTEP`

## Dependencies

- `<stddef.h>`
- `bitstream.h` in static-link-only mode.

## Research Notes

- Encoding and decoding are reverse-order by design.
- Fast decode requires no symbol with probability over 50%.
- Table sizing macros are part of the internal ABI used by Zstd sequence coding.
- The public API deliberately does not handle raw/RLE data in `FSE_decompress`; callers must handle those cases.
