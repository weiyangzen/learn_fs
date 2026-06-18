# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_compress.c

## Purpose

Huffman encoder implementation for Zstd literal compression. It builds canonical Huffman tables, serializes table weights, and encodes data as one stream or four parallel streams.

## Main Components

- Utility:
  - `HUF_optimalTableLog`
  - `HUF_compressBound`
  - `HUF_getNbBits`
- Weight/table serialization:
  - `HUF_compressWeights`
  - `HUF_writeCTable`
  - `HUF_readCTable`
- CTable construction:
  - `HUF_setMaxHeight`
  - `HUF_sort`
  - `HUF_buildCTable_wksp`
  - `HUF_buildCTable`
- CTable analysis:
  - `HUF_estimateCompressedSize`
  - `HUF_validateCTable`
- Bitstream encoding:
  - `HUF_encodeSymbol`
  - `HUF_compress1X_usingCTable_internal_body`
  - `HUF_compress1X_usingCTable`
  - `HUF_compress4X_usingCTable_internal`
  - `HUF_compress4X_usingCTable`
- High-level compression:
  - `HUF_compress_internal`
  - `HUF_compress1X_wksp`
  - `HUF_compress1X_repeat`
  - `HUF_compress1X`
  - `HUF_compress4X_wksp`
  - `HUF_compress4X_repeat`
  - `HUF_compress2`
  - `HUF_compress`

## Behavior

- Counts input with `HIST_count_wksp`.
- Returns RLE marker size `1` when input is a single repeated byte.
- Rejects likely incompressible data via frequency and final-size heuristics.
- Builds a Huffman tree from sorted frequencies, then limits maximum bit height with `HUF_setMaxHeight`.
- Serializes Huffman weights using FSE when beneficial, otherwise raw 4-bit packed weights.
- Four-stream compression writes a 6-byte jump table containing the first three stream sizes.

## Dependencies

- `compiler.h`
- `bitstream.h`
- `hist.h`
- `fse.h`
- `huf.h`
- `error_private.h`

## Research Notes

- Dynamic BMI2 wrappers compile specialized bodies only when `DYNAMIC_BMI2` is enabled.
- Repeat-table paths can reuse a previous Huffman table when valid and estimated cheaper.
- The compressor requires source blocks no larger than `HUF_BLOCKSIZE_MAX` and workspace aligned on 4-byte boundaries.
