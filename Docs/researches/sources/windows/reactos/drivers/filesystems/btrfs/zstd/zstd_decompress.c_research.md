# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_decompress.c

## Summary
Implements the main zstd decompression context, one-shot decompression, frame parsing, dictionary loading, and streaming decompression state machine.

## Key APIs
- Context lifecycle: `ZSTD_createDCtx()`, `ZSTD_createDCtx_advanced()`, `ZSTD_initStaticDCtx()`, `ZSTD_freeDCtx()`, `ZSTD_sizeof_DCtx()`.
- Frame inspection: `ZSTD_isFrame()`, `ZSTD_frameHeaderSize()`, `ZSTD_getFrameHeader()`, `ZSTD_getFrameContentSize()`, `ZSTD_findFrameCompressedSize()`, `ZSTD_decompressBound()`.
- One-shot decompression: `ZSTD_decompress()`, `ZSTD_decompressDCtx()`, `ZSTD_decompress_usingDict()`, `ZSTD_decompress_usingDDict()`.
- Dictionary/session setup: `ZSTD_decompressBegin*()`, `ZSTD_loadDEntropy()`, `ZSTD_getDictID_fromDict()`, `ZSTD_getDictID_fromFrame()`.
- Streaming APIs: `ZSTD_createDStream*()`, `ZSTD_initDStream*()`, `ZSTD_decompressStream()`, `ZSTD_decompressContinue()`, `ZSTD_DCtx_setParameter()`, `ZSTD_DCtx_reset()`.

## Important Behavior
Frame parsing handles normal, magicless, skippable, and optionally legacy frames. It validates reserved header bits, window limits, frame content size, dictionary ID, block sizes, and checksums. One-shot decompression iterates across multiple frames, skips skippable frames, initializes dictionary state per frame, dispatches compressed blocks to `ZSTD_decompressBlock_internal()`, and handles raw/RLE blocks locally.

Streaming decompression layers a higher-level `zdss_*` state machine over the lower-level `ZSTDds_*` frame/block stages. It buffers input and output as required by window size, supports stable-output mode, opportunistically shortcuts complete known-size frames into one-shot mode, limits maximum window memory, and detects repeated no-progress calls.

## Risks
Static contexts cannot grow buffers beyond the supplied workspace and are incompatible with legacy streaming support. The streaming code has many state-dependent invariants: output-buffer stability, hostage-byte handling, input position accounting, and dictionary use-once semantics all must be preserved by callers.
