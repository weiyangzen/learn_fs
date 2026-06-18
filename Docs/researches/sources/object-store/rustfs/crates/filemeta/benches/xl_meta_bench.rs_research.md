# sources/object-store/rustfs/crates/filemeta/benches/xl_meta_bench.rs

Purpose: Criterion benchmark suite for the XL metadata hot path in `rustfs-filemeta`.

Important APIs and flow: benchmarks call `test_data::{create_real_xlmeta, create_complex_xlmeta}`, parse with `FileMeta::load`, serialize with `marshal_msg`, run load/serialize/load round trips, compute `get_version_stats`, and call `validate_integrity`. `black_box` prevents compiler elimination.

State and persistence: all data is generated in memory from test fixtures. Benchmarks measure the same serialized XL metadata bytes persisted on disk but do not write files.

Dependencies and integration: depends on Criterion and public `rustfs_filemeta` APIs. It provides performance signals for storage paths that repeatedly parse or rewrite `xl.meta`.

Risks: generated fixture realism controls benchmark value. No explicit throughput thresholds are enforced, so regressions require comparing Criterion history. The suite benchmarks synchronous parse/serialize, not async disk read or object-store end-to-end behavior.

Test signals: named benchmark functions cover real and complex metadata creation, parsing, serialization, round-trip, stats, and integrity validation.
