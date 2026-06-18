# sources/object-store/rustfs/crates/utils/src/compress.rs

Purpose: Block compression/decompression helpers for several algorithms.

Important APIs: `CompressionAlgorithm` enum (`None`, `Gzip`, `Deflate`, `Zstd`, default `Lz4`, `Brotli`, `Snappy`) with `as_str`, `Display`, and `FromStr`; `compress_block`; `decompress_block`.

Control flow: Compression dispatches to the selected library writer/encoder and returns compressed bytes. Decompression dispatches to matching readers/decoders. `None` compression returns the input bytes, while `None` decompression returns an empty vector.

State and dependencies: Stateless. Depends on `flate2`, `zstd`, `lz4`, `brotli`, `snap`, `tokio::io` for error type, and std I/O.

Integration points: Enabled by the utils `compress` feature. Tests exercise round-trip behavior for all actual algorithms and print benchmark/comparison output.

Risks and tests: Several compression paths ignore `write_all`/`flush` errors or use `expect`, making some failures panic or degrade to empty output. `decompress_block(None)` returning empty instead of original bytes is a semantic trap if callers treat `None` as pass-through. Benchmark tests print timing and may be noisy but assert round-trip correctness.
