# sources/object-store/rustfs/crates/ecstore/benches/single_block_non_inline_benchmark.rs

Purpose: Criterion benchmark comparing the general erasure encode pipeline with a `encode_single_block_non_inline` fast-path candidate for small payloads that still use non-inline writers.

Important APIs and types: `BenchConfig` describes payload size, data/parity shard counts, and block size. `build_non_inline_writers` creates `BitrotWriterWrapper` instances around `tokio::io::sink()` using `CustomWriter::new_tokio_writer` and `HashAlgorithm::HighwayHash256S`. Benchmarks call `Erasure::encode` and `Erasure::encode_single_block_non_inline`.

Control flow: a current-thread Tokio runtime is embedded in the benchmark. For each 4 KiB, 64 KiB, and 128 KiB payload, it creates fresh non-inline writers and a `BufReader<Cursor<Vec<u8>>>`, then blocks on the async encode method.

State and persistence: no durable writes because all shard output goes to `tokio::io::sink`; bitrot wrapping and shard sizing are still exercised.

Dependencies and integration points: integrates erasure coding, bitrot writer wrappers, Tokio async IO, Criterion, and RustFS hash algorithms.

Risks: sink writers exclude real disk latency and filesystem allocation behavior. Cloning payloads and writer construction are part of measured work.

Test signals: focused performance signal for deciding whether the single-block non-inline path improves small-object write throughput.
