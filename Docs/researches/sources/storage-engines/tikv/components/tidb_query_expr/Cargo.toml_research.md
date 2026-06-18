# sources/storage-engines/tikv/components/tidb_query_expr/Cargo.toml

## Purpose

This manifest defines the `tidb_query_expr` crate, which provides vectorized expression evaluation for TiDB pushed-down executors in TiKV. The crate is private to the workspace (`publish = false`), uses Rust 2021, and is licensed Apache-2.0.

## Important APIs, Types, and Functions

As a `Cargo.toml`, this file does not define Rust APIs directly. Its important contract is dependency and crate metadata configuration:

- Package: `tidb_query_expr`, version `0.0.1`, description "Vector expressions of query engine to run TiDB pushed down executors".
- Workspace dependencies include `codec`, `crypto`, `file_system`, `log_wrappers`, `openssl`, `tidb_query_codegen`, `tidb_query_common`, `tidb_query_datatype`, `tikv_util`, `time`, `tipb`, `chrono`, and test-only `panic_hook`/`profiler`.
- External dependencies include serialization/parsing/utility crates such as `base64`, `bstr`, `byteorder`, `chrono-tz`, `flate2` pinned to `=1.0.11` with zlib, `hex`, `match-template`, `memchr`, `num`, `num-traits`, `protobuf`, `rand`, `regex`, `serde`, `serde_json`, `static_assertions` with nightly feature, and `uuid`.

## Control Flow

There is no runtime control flow. Cargo uses this manifest to resolve dependencies, compile the expression crate, and compile dev-only test support. Feature flow is limited to dependency feature selection such as `flate2` using zlib and `uuid` enabling `v1`, `v4`, and `std`.

## State and Persistence Behavior

The manifest has no runtime state. It affects build reproducibility and dependency graph state through exact or semver dependency constraints. The pinned `flate2 = "=1.0.11"` is a notable reproducibility constraint.

## Dependencies and Integration Points

`tidb_query_expr` is a core integration crate for executor files in this work item. Aggregation, TopN, and utility modules use `RpnExpression`, `RpnExpressionBuilder`, `RpnStackNode`, arithmetic/operator function metadata, and expression support checking from this crate. The manifest links expression evaluation to datatype codecs, common query errors/results, generated aggregate/function code, protobuf Tipb expressions, logging wrappers, crypto/file utilities, and serialization libraries.

## Risks and Edge Cases

- `static_assertions` enables a `nightly` feature, which may constrain toolchain compatibility.
- Exact `flate2` pinning may be intentional for compatibility but can delay security or bugfix updates.
- Broad dependencies such as `openssl`, `regex`, `serde_json`, and `uuid` increase build surface for a low-level expression crate.
- Workspace dependency versions are controlled outside this file, so compatibility must be reviewed with the workspace manifest.

## Test Signals

Dev dependencies `tipb_helper`, `panic_hook`, `profiler`, and duplicate `bstr`/`chrono` entries support unit tests and profiling in the expression crate. The executor tests in this work item indirectly validate `tidb_query_expr` behavior through RPN expression construction, support checking, decoded evaluation, scalar/vector outputs, collation-aware comparison, arithmetic, and null tests.
