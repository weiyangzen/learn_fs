# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_superblock.c

## Summary
Implements Zstandard "super block" compression for `targetCBlockSize`, where a larger block's literals and sequences share one entropy model and are emitted as multiple compressed sub-blocks near the target compressed size.

## Key APIs
- Exports `ZSTD_compressSuperBlock()`.
- Internal builders: `ZSTD_buildSuperBlockEntropy_literal()`, `ZSTD_buildSuperBlockEntropy_sequences()`, `ZSTD_buildSuperBlockEntropy()`.
- Internal emitters/estimators: `ZSTD_compressSubBlock_literal()`, `ZSTD_compressSubBlock_sequences()`, `ZSTD_compressSubBlock()`, `ZSTD_compressSubBlock_multi()`, and sub-block size estimators.

## Important Behavior
Literal entropy construction chooses raw, RLE, repeat, or compressed Huffman tables based on literal size, symbol frequency, previous-table validity, estimated compressed size, and disabled-literal-compression settings. Sequence entropy construction converts sequences to codes, builds/selects LL/OF/ML FSE tables, and stores compact table metadata for later sub-block headers.

Sub-block emission writes entropy only once, then uses repeat modes for following sub-blocks. It estimates compressed sub-block size while scanning sequences, commits a compressed sub-block only when the result is smaller than its decompressed span, and falls back to raw blocks for any uncompressed tail. If required entropy tables were never written, it returns 0 so the caller can choose an uncompressed block path.

## Risks
The code has several intentionally conservative fallbacks for old zstd decoder bugs: tiny FSE table/bitstream combinations and sequence sections shorter than four bytes become uncompressed output outside fuzzing builds. Correctness depends on the fixed 500-byte entropy metadata buffers and on `zc->entropyWorkspace` being large enough for `HUF_WORKSPACE_SIZE`.
