# sources/storage-engines/tikv/components/pd_client/src/errors.rs

## Purpose
`errors.rs` defines the PD client error type, retryability classification, and error-code mapping.

## Important APIs, Types, and Functions
- `Error` variants cover cluster bootstrap state, incompatible features, grpc errors, stream disconnects, boxed errors, missing regions, tombstone stores, compacted watch data, and unsafe service GC safe point updates.
- `Result<T>` aliases `std::result::Result<T, Error>`.
- `retryable` marks grpc, cluster-not-bootstrapped, stream disconnect, and data-compacted errors as retryable.
- `ErrorCodeExt` maps each variant to `error_code::pd::*`.

## Control Flow
Retryability and error-code mapping are direct matches over the enum. Conversions from `grpcio::Error`, futures mpsc `SendError`, and boxed errors are provided through `thiserror`.

## State and Persistence Behavior
No state. Errors may carry keys, timestamps, or formatted store data used in logs/responses.

## Dependencies and Integration Points
Uses `error_code`, `futures::channel::mpsc::SendError`, `grpcio`, `log_wrappers::Value` for redacted/hex key display, and `txn_types::TimeStamp`.

## Risks
Retry classification influences request loops; marking non-idempotent or semantic errors retryable would be dangerous, while missing transient errors reduces availability. `StoreTombstone` stores a formatted string, not the structured store. `Other` loses specific error-code detail and maps to unknown.

## Test Signals
No local tests. Behavior is exercised through PD request callers and error-code reporting.
