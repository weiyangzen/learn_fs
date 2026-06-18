# sources/storage-engines/tikv/components/tidb_query_executors/src/lib.rs

## Purpose
`lib.rs` is the crate root for TiKV's `tidb_query_executors` component. It configures nightly Rust features/macros, declares executor modules, exposes common test-only query expression/aggregration imports, and re-exports the public batch executor types used by runner/planner code.

## Important APIs, Types, and Functions
- Crate-level feature gates: `proc_macro_hygiene`, `specialization`, and `stmt_expr_attributes`, with `incomplete_features` allowed.
- Macro imports: `tikv_util` macros `box_try` and `warn`, and `tidb_query_common` macro `other_err`.
- Public modules: `interface` and `runner`.
- Private executor/util modules: fast/slow hash aggregation, simple/stream aggregation, index lookup, index scan, limit, partition top-n, projection, selection, table scan, top-n, and `util`.
- Public re-exports: `BatchFastHashAggregationExecutor`, `BatchIndexLookUpExecutor`, `BatchIndexScanExecutor`, `BatchLimitExecutor`, `BatchPartitionTopNExecutor`, `BatchProjectionExecutor`, `BatchSelectionExecutor`, `BatchSimpleAggregationExecutor`, `BatchSlowHashAggregationExecutor`, `BatchStreamAggregationExecutor`, `BatchTableScanExecutor`, and `BatchTopNExecutor`.

## Control Flow
There is no runtime control flow in this file. Its main job is compile-time crate assembly. Rust module declarations bring implementation files into the crate, and the final `pub use self::{...}` block defines the crate's external executor surface. Code outside the crate imports executor types from this root rather than from private module paths.

## State and Persistence Behavior
This file maintains no runtime state and performs no persistence. Its state effect is namespace-level: it determines which modules are compiled and which executor types are exported.

## Dependencies and Integration Points
- Integrates with the broader TiKV query stack by exporting executor types that implement the `BatchExecutor` trait from `interface.rs`.
- Test-only re-exports from `tidb_query_aggr` and `tidb_query_expr` simplify in-crate tests for executor expression/aggregation behavior.
- `runner` is public and likely coordinates construction/execution of the exported executors for coprocessor requests.

## Risks and Edge Cases
- Public API changes here have broad impact because downstream code imports executor types through crate-root re-exports.
- Feature gates tie the crate to nightly-only behavior. Removing or changing them may affect macro expansion, specialization, or statement expression attributes used elsewhere in the crate.
- Private module visibility means new executors must be both declared and explicitly re-exported if they are intended for external use.
- Test-only re-exports are gated by `#[cfg(test)]`; non-test code cannot depend on those symbols through this crate root.

## Test Signals
`lib.rs` contains no tests. Its validation is primarily compile-level: all declared modules must compile, exported executor names must resolve, and crate tests that import test-only expression/aggr helpers through the root must build.
