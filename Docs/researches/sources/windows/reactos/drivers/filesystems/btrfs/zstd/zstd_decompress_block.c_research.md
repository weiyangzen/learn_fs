# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_decompress_block.c

## Summary
Implements decompression of zstd compressed blocks: block header sizing, literal section decoding, FSE sequence-table construction, sequence decoding, and literal/match execution.

## Key APIs
- `ZSTD_getcBlockSize()`.
- `ZSTD_decodeLiteralsBlock()`.
- `ZSTD_buildFSETable()`.
- `ZSTD_decodeSeqHeaders()`.
- `ZSTD_decompressBlock_internal()`.
- `ZSTD_checkContinuity()`.
- `ZSTD_decompressBlock()`.

## Important Behavior
Literal decoding supports repeat, compressed, raw/basic, and RLE literal sections. Compressed literals use Huffman tables from the current block or prior entropy state, with dictionary-table prefetching when a DDict is cold. Sequence headers decode the number of sequences and LL/OF/ML encoding modes, then build or select default, RLE, repeat, or compressed FSE decode tables.

Sequence execution decodes literal length, match length, and offset codes from a bitstream, maintains repeat offsets, and copies literals and matches into the output. Fast paths use wildcopy and overlap-specialized copies; edge paths perform stricter bounds checks near the end of the buffer or when matches cross from an external dictionary into the current prefix. A second "long" sequence decoder prefetches match locations when long offsets or cold dictionaries make cache misses likely.

## Risks
Most functions operate on trusted internal invariants after initial validation; malformed input is caught through explicit corruption, source-size, and destination-size checks. Copy paths deliberately read/write within zstd's wildcopy overrun allowances, so callers must provide the expected block buffers and capacities.
