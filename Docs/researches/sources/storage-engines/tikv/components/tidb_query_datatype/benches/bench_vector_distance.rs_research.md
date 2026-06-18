# sources/storage-engines/tikv/components/tidb_query_datatype/benches/bench_vector_distance.rs

## Purpose
Provides Criterion microbenchmarks for vector distance and norm operations on `VectorFloat32Ref`, covering small 3-dimensional vectors and larger 784-dimensional vectors.

## APIs, Flow, And State
Each benchmark builds one or two `Vec<f32>` values, converts them through `VectorFloat32Ref::from_f32`, and benchmarks a single method inside `black_box`: `l1_distance`, `l2_squared_distance`, `l2_distance`, `inner_product`, `cosine_distance`, or `l2_norm`. `criterion_group!` registers all twelve benchmark functions and `criterion_main!` supplies the harness.

## Dependencies And Integration
Depends on `criterion` and `tidb_query_datatype::codec::mysql::VectorFloat32Ref`. It is wired by the crate manifest as `bench_vector_distance`.

## Risks And Test Signals
Benchmarks use identical input vectors, so they measure hot-path arithmetic and decoding-free vector reference overhead, not mismatched dimensions or error paths. They are performance signals, not correctness tests; correctness is implied by unwraps and by separate vector datatype tests elsewhere.
