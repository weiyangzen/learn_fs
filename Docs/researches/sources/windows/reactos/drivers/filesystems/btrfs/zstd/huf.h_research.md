# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf.h

## Purpose

Public and static-link API header for Huffman entropy compression/decompression used by Zstd literals.

## Main Components

- Public API:
  - `HUF_compress`
  - `HUF_decompress`
  - `HUF_compressBound`
  - `HUF_isError`
  - `HUF_getErrorName`
  - `HUF_compress2`
  - `HUF_compress4X_wksp`
- Public constants:
  - `HUF_BLOCKSIZE_MAX`
  - `HUF_WORKSPACE_SIZE`
  - `HUF_WORKSPACE_SIZE_U32`
- Static-link constants:
  - `HUF_TABLELOG_MAX`
  - `HUF_TABLELOG_DEFAULT`
  - `HUF_SYMBOLVALUE_MAX`
  - `HUF_TABLELOG_ABSOLUTEMAX`
  - `HUF_CTABLEBOUND`
  - `HUF_COMPRESSBOUND`
- Table allocation macros:
  - `HUF_CTABLE_SIZE_U32`
  - `HUF_CREATE_STATIC_CTABLE`
  - `HUF_DTABLE_SIZE`
  - `HUF_CREATE_STATIC_DTABLEX1`
  - `HUF_CREATE_STATIC_DTABLEX2`
- Compression internals:
  - `HUF_optimalTableLog`
  - `HUF_buildCTable`
  - `HUF_writeCTable`
  - `HUF_readCTable`
  - `HUF_compress1X/4X`
  - repeat-table APIs
- Decompression internals:
  - `HUF_readStats`
  - `HUF_selectDecoder`
  - `HUF_readDTableX1/X2`
  - `HUF_decompress1X/4X`
  - BMI2-aware wrappers.

## Behavior

- Supports both single-stream and four-stream Huffman coding.
- Supports X1 single-symbol and X2 double-symbol decode table formats.
- Public `HUF_decompress` handles raw and RLE cases because original size is known.

## Research Notes

- The static-link section is explicitly unstable and not suitable for dynamic-library ABI.
- Many APIs require exact compressed and decompressed sizes.
- Decoder selection is heuristic unless `HUF_FORCE_DECOMPRESS_X1` or `HUF_FORCE_DECOMPRESS_X2` is defined.
