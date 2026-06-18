# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_superblock.h

## Summary
Declares the super-block compression entry point used when target compressed block sizing is enabled.

## Key APIs
- `ZSTD_compressSuperBlock(ZSTD_CCtx* zc, void* dst, size_t dstCapacity, void const* src, size_t srcSize, unsigned lastBlock)`.

## Important Behavior
The header depends on `zstd.h` for `ZSTD_CCtx` and exposes only one function. The implementation compresses one input block into multiple compressed sub-blocks that share super-block entropy and are sized around the active `targetCBlockSize`.

## Risks
This is an internal advanced-compression interface. Callers must pass a fully initialized compression context with populated sequence store, block state, applied parameters, BMI2 flag, and entropy workspace.
