# sources/object-store/rustfs/crates/ecstore/benches/erasure_benchmark.rs

Purpose: Criterion benchmark suite comparing ecstore erasure encode/decode performance and selected direct `reed_solomon_erasure` paths.

Important APIs and types: `BenchConfig` captures data shard count, parity shard count, data size, block size, and a display name. `generate_test_data` creates deterministic payloads. Benchmarks call `Erasure::encode_data`, `Erasure::decode_data`, and `calc_shard_size`.

Control flow: encode benchmarks run SIMD ecstore implementation for configurations from 1 KiB through 16 MiB, then optionally benchmark direct `reed_solomon_erasure::galois_8::ReedSolomon` when shard size is at least 512 bytes. Decode benchmarks pre-encode, remove one data and one parity shard, then reconstruct. Additional groups measure shard-size impact, coding-configuration impact, and reuse of an `Erasure` instance.

State and persistence: no application state. Criterion persists benchmark measurements and reports externally under target output.

Dependencies and integration points: benchmarks the public erasure-coding module and optionally direct Reed-Solomon library behavior for comparison.

Risks: direct comparison paths do not include all wrapper behavior and may not be apples-to-apples. Some benchmark names mention SIMD even when overhead includes buffer allocation and wrapper setup.

Test signals: performance regression detector for data-size scaling, shard-count scaling, decode reconstruction, and memory pattern costs.
