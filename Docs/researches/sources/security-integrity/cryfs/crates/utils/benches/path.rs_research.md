# sources/security-integrity/cryfs/crates/utils/benches/path.rs

Purpose: criterion benchmark comparing `cryfs_utils::path::path_join` against standard `PathBuf` joining strategies.

Important APIs/types/functions: `bench_join(c: &mut Criterion)` benchmarks `path_join`, chained `PathBuf::join`, `PathBuf::extend`, and repeated `PathBuf::push` over absolute and relative paths with double slashes.

Control flow/state: creates black-boxed path inputs, registers four benchmark functions, and uses criterion macros to define the benchmark main.

Dependencies/integration: depends on `criterion`, `std::hint::black_box`, and `cryfs_utils::path::path_join`.

Risks: benchmark inputs include absolute middle components, so behavior follows `PathBuf::push` reset semantics. Results are performance signals only, not correctness proof.

Test signals: complements unit tests in `path/join.rs` by measuring allocation/performance intent.
