# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_decompress.c

## Purpose

Huffman decoder implementation for Zstd literals. It builds X1 and X2 decode tables, decodes one-stream and four-stream payloads, handles raw/RLE shortcuts, and selects decoder variants using precomputed heuristics.

## Main Components

- Table metadata:
  - `DTableDesc`
  - `HUF_getDTableDesc`
- BMI2 wrappers:
  - `HUF_DGEN`
- X1 single-symbol decoder:
  - `HUF_DEltX1`
  - `HUF_readDTableX1_wksp`
  - `HUF_readDTableX1`
  - `HUF_decodeSymbolX1`
  - `HUF_decodeStreamX1`
  - `HUF_decompress1X1_usingDTable_internal_body`
  - `HUF_decompress4X1_usingDTable_internal_body`
  - public/DCtx wrappers
- X2 double-symbol decoder:
  - `HUF_DEltX2`
  - `sortedSymbol_t`
  - `rankVal_t`
  - `HUF_fillDTableX2Level2`
  - `HUF_fillDTableX2`
  - `HUF_readDTableX2_wksp`
  - `HUF_readDTableX2`
  - `HUF_decodeSymbolX2`
  - `HUF_decodeLastSymbolX2`
  - `HUF_decodeStreamX2`
  - `HUF_decompress1X2_usingDTable_internal_body`
  - `HUF_decompress4X2_usingDTable_internal_body`
  - public/DCtx wrappers
- Selector and universal APIs:
  - `HUF_decompress1X_usingDTable`
  - `HUF_decompress4X_usingDTable`
  - `HUF_selectDecoder`
  - `HUF_decompress`
  - `HUF_decompress4X_DCtx`
  - `HUF_decompress4X_hufOnly`
  - `HUF_decompress1X_DCtx`
  - BMI2 variants.

## Behavior

- Reads Huffman weights via `HUF_readStats`.
- X1 tables map bit prefixes to one byte and bit length.
- X2 tables can emit one or two bytes per lookup.
- Four-stream decoding reads a 6-byte jump table, initializes four `BIT_DStream_t` streams, decodes segments in parallel, then validates all streams ended exactly.
- `HUF_decompress` treats `cSrcSize == dstSize` as raw copy and `cSrcSize == 1` as RLE fill.
- `HUF_decompress4X_hufOnly*` rejects raw/RLE shortcuts and expects a real Huffman payload.

## Dependencies

- `compiler.h`
- `bitstream.h`
- `fse.h`
- `huf.h`
- `error_private.h`

## Research Notes

- `HUF_selectDecoder` chooses X1 or X2 using a static timing table based on compression ratio and output size.
- Workspace layout in `HUF_readDTableX1_wksp` and `HUF_readDTableX2_wksp` is manually packed and alignment-sensitive.
- Corruption checks include stream size bounds, segment overflow, output segment overrun, and exact bitstream completion.
