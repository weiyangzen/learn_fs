# sources/storage-engines/tikv/src/import/mod.rs

## Purpose
Defines the import module boundary for TiDB Lightning/BR SST import support and common RPC error/metric helpers.

## Important APIs, Types, and Functions
Declares internal modules `duplicate_detect`, `ingest`, `raft_writer`, and `sst_service`. Re-exports `sst_importer::{Config, Error, Result, SstImporter, TxnSstWriter}` and `ImportSstService`. `make_rpc_error` converts debug-printable errors into gRPC unknown statuses. `send_rpc_response!` records RPC duration, increments error metrics, and sends success/failure to a sink. `pb_error_inc` classifies `errorpb::Error` variants into importer metric labels.

## Control Flow
RPC handlers use `send_rpc_response!` to normalize response sending and duration recording. Store-region errors are classified by `pb_error_inc` for metrics. There is no service control flow here beyond helper macro expansion.

## State and Persistence Behavior
No local persistent state. Metrics are updated through `IMPORT_RPC_DURATION` and `IMPORTER_ERROR_VEC`.

## Dependencies and Integration Points
Integrates gRPC (`grpcio`), kvproto region errors, sst importer metrics/types, and the concrete `ImportSstService`. This is the public import facade for the crate.

## Risks and Edge Cases
`make_rpc_error` uses debug formatting and always maps to UNKNOWN, which can be unfriendly to clients. Macro users must pass consistent label/timer variables. `pb_error_inc` has a fixed classification list; new region error variants fall into `unknown` until updated.

## Test Signals
No direct tests. Metric classification and macro behavior are covered only through RPC paths that invoke them.
