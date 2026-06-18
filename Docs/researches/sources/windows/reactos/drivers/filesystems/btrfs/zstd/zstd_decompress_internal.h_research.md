# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_decompress_internal.h

## Summary
Defines shared decompression constants, entropy table types, decompression stages, dictionary-use modes, output-buffer modes, and the full `ZSTD_DCtx_s` structure.

## Key APIs
- Constants: `LL_base`, `OF_base`, `OF_bits`, `ML_base`.
- Types: `ZSTD_seqSymbol_header`, `ZSTD_seqSymbol`, `ZSTD_entropyDTables_t`, `ZSTD_dStage`, `ZSTD_dStreamStage`, `ZSTD_dictUses_e`, `ZSTD_outBufferMode_e`, `ZSTD_DCtx_s`.
- Shared functions: `ZSTD_loadDEntropy()`, `ZSTD_checkContinuity()`.

## Important Behavior
The base/additional-bit tables define how LL, OF, and ML FSE symbols map to concrete sequence values. `ZSTD_entropyDTables_t` stores LL/OF/ML decode tables, a Huffman decode table, and repeat offsets. `ZSTD_DCtx_s` combines entropy state, literal/header work buffers, frame metadata, dictionary bounds, one-shot block state, streaming buffers, legacy context pointers, output stability state, and fuzzing-only dictionary bounds.

## Risks
This header exposes layout-sensitive internals used across decompression modules. Changes to table sizes, field ordering, or stage semantics affect dictionary loading, block decoding, streaming, and memory accounting.
