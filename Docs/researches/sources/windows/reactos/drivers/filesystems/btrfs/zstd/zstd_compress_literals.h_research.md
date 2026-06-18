# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.h

## Role

Private header declaring literal compression helpers used by the zstd compression pipeline.

## Exposed Functions

- `ZSTD_noCompressLiterals()`
  - Emits raw literal sections.
- `ZSTD_compressRleLiteralsBlock()`
  - Emits RLE literal sections.
- `ZSTD_compressLiterals()`
  - Selects and emits raw, RLE, repeated-table, or Huffman-compressed literal sections.

## Dependencies

- Includes `zstd_compress_internal.h` for:
  - `ZSTD_hufCTables_t`
  - `ZSTD_minGain()`
  - zstd strategy and internal block-format types

## ReactOS/Btrfs Relevance

This header connects the main compressor to the literal-section encoder used for Btrfs zstd block/frame compression.

## Risks and Notes

- The API is internal, not a stable external interface.
- Callers must pass valid previous/next Huffman table state and an adequately sized entropy workspace.
