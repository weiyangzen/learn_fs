# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/mod.rs

## Purpose
This module is the shared utility root for coprocessor executor benchmarks.

## Important APIs, Types, and Functions
It re-exports `FixtureBuilder`, declares utility submodules, provides `bench_level()` from `TIKV_BENCH_LEVEL`, and defines `build_dag_handler` for constructing `DagHandlerBuilder<ApiV1>`. It also defines generic `BenchCase` storage through `InnerBenchCase`, `IBenchCase`, and `BenchCase`.

## Control Flow
`build_dag_handler` builds a `DagRequest`, copies executor descriptors and key ranges, converts the test store to the requested transaction store type, supplies a deadline and quota limiter, and returns a boxed request handler. `BenchCase` boxes benchmark functions, exposes names/functions, and implements ordering by name for deterministic Criterion output.

## State and Persistence Behavior
The module holds no persistent state. DAG handler construction consumes caller-provided stores/ranges and creates per-benchmark request state.

## Dependencies and Integration Points
It depends on API V1, Criterion, `test_coprocessor`, TiKV coprocessor DAG handler APIs, `StubAccessor`, `QuotaLimiter`, and `tipb` descriptors. All coprocessor executor benchmark families use it.

## Risks and Test Signals
`bench_level` uses `unwrap()` on parse, so invalid environment values panic. DAG builder parameters such as deadline, batch flags, and concurrency defaults can affect benchmark comparability. Successful use by all child modules validates the shared harness.
