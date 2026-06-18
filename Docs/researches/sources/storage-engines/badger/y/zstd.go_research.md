# sources/storage-engines/badger/y/zstd.go

## Purpose
This file wraps `klauspost/compress/zstd` compression and decompression for Badger blocks and provides a compression-bound estimate.

## Important APIs, Types, And Functions
Global `decoder` and `encoder` are initialized lazily by `sync.Once`. `ZSTDDecompress` calls `DecodeAll`. `ZSTDCompress` maps an integer level to a zstd encoder level and calls `EncodeAll`. `ZSTDCompressBound` estimates the worst-case output size using a DataDog-derived formula.

## Control Flow
The first compress/decompress call initializes the shared codec and fatals via `Check` on construction error. Subsequent calls reuse the codec. Both APIs append into `dst[:0]`.

## State And Persistence Behavior
The code holds process-global encoder/decoder state. Compressed bytes may be persisted in Badger tables depending on compression options.

## Dependencies And Integration Points
It depends on `github.com/klauspost/compress/zstd` and Badger error helpers. Table/block compression code calls these wrappers.

## Risks And Edge Cases
The encoder is created only once, so later calls with different compression levels reuse the first level. Shared encoder/decoder concurrency safety depends on the library's `EncodeAll`/`DecodeAll` guarantees. Construction errors terminate the process.

## Test Signals
No direct tests in this subset. Compression integration tests elsewhere should catch round-trip or sizing regressions.
