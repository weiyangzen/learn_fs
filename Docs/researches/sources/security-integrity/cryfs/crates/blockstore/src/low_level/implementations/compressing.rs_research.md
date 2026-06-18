<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/compressing.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/compressing.rs

## Purpose
Implements a low-level blockstore decorator that LZ4-frame compresses block payloads before storage and decompresses them on load. The file notes it is currently intended for tests rather than optimized production use.

## APIs, Flow, And State
`CompressingBlockStore<B>` owns an underlying async-drop store. Reads delegate `exists`, count, free-space, overhead, and all-blocks; `load` fetches compressed data then `_decompress`es it with `tokio::task::spawn_blocking`. Writes implement `OptimizedBlockStoreWriter` by extracting data, `_compress`ing it with `lzzzz::lz4f`, and forwarding to non-optimized `try_create`/`store` because compressed sizes do not preserve prefix-space assumptions. `AsyncDrop` delegates to the underlying store.

## Dependencies And Integration
Requires underlying reader/deleter/optimized-writer traits as appropriate. It composes with any `LLBlockStore + OptimizedBlockStoreWriter` and participates in generic low-level blockstore tests over `InMemoryBlockStore`.

## Risks And Test Signals
Reported overhead ignores compression and can be inaccurate, especially because compression can reduce physical size. Compression/decompression errors propagate with context on load. Tests run the generic low-level suite and verify overhead conversion with zero added overhead.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/compressing.rs -->
