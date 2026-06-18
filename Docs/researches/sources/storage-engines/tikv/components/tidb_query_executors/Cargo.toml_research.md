# sources/storage-engines/tikv/components/tidb_query_executors/Cargo.toml

## Purpose
This manifest defines the `tidb_query_executors` crate, described as a vector query engine for TiDB pushed-down executors.

## Important APIs, types, and functions
The package is version `0.0.1`, edition `2021`, unpublished, and Apache-2.0 licensed. Runtime dependencies include async support, workspace codec/collections/kvproto/tipb/txn types, `tidb_query_aggr`, `tidb_query_common`, `tidb_query_datatype`, `tidb_query_expr`, metrics/logging utilities, `match-template`, `protobuf`, `smallvec`, and `fail`.

## Control flow
No runtime control flow exists in the manifest, but feature and dependency choices determine available executor implementations and test utilities.

## State and persistence behavior
The manifest has no runtime state.

## Dependencies and integration points
This crate sits above datatype, expression, common storage interfaces, and aggregation crates. Dev dependencies `anyhow`, `tidb_query_codegen`, and `tipb_helper` support executor tests and expression construction.

## Risks and edge cases
The manifest does not declare crate-local features, so optional behavior is mostly controlled by code cfgs and workspace dependency versions. Executor code relies on workspace versions of core TiKV crates, making API drift in those crates a direct integration risk.

## Test signals
The dev dependencies align with the test modules in executor files that use `tipb_helper`, mock storage, and generated query function support.
