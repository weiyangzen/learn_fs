# sources/object-store/rustfs/crates/ecstore/benches/comparison_benchmark.rs

Purpose: Criterion performance analysis for the SIMD-backed `rustfs_ecstore::erasure_coding::Erasure` implementation across sizes, shard layouts, recovery cases, concurrency, and instance reuse.

Important APIs and functions: `TestData` builds deterministic byte vectors. `generate_test_datasets` spans 1 KiB to 4 MiB. Benchmark functions cover encode, decode, shard-size sensitivity, concurrent encode from four threads, error recovery under different loss counts, and memory/instance reuse.

Control flow: each benchmark constructs `Erasure::new(data_shards, parity_shards, len)`, pre-validates whether `encode_data` supports the configuration, and then uses Criterion groups with explicit sample sizes and measurement durations. Decode and recovery benchmarks convert encoded shards into `Vec<Option<Vec<u8>>>`, drop selected shards, and call `decode_data`.

State and persistence: no persistent state; Criterion writes result artifacts under `target/criterion` when executed.

Dependencies and integration points: depends on Criterion, standard `black_box`, threads for concurrency, and the ecstore erasure module.

Risks: many iterations allocate cloned shard vectors, so results include allocation cost, not pure Reed-Solomon math. Skipped unsupported configurations print warnings instead of failing, which is useful for portability but can hide lost coverage.

Test signals: useful baseline for SIMD erasure throughput, decode recovery cost, shard-size thresholds, and reuse-vs-new instance overhead.
