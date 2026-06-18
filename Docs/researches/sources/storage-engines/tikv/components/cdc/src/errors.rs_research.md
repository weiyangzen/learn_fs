# sources/storage-engines/tikv/components/cdc/src/errors.rs

## Purpose

`errors.rs` defines the CDC subsystem error type and maps internal TiKV/engine/sink/memory errors into CDC protobuf error events sent to clients. It centralizes region-error detection so initializer and endpoint code can decide whether to deregister an entire delegate or only one downstream.

## Important APIs, Types, And Functions

- `Error` enum wraps generic boxed errors, RocksDB string errors, IO errors, storage KV errors, transaction errors, MVCC errors, raftstore request errors, engine-traits errors, CDC sink errors, and memory quota failures.
- `impl_from!` adds conversions from `String` to `Error::Rocks` and `txn_types::Error` to `Error::Mvcc`.
- `Result<T>` is the CDC-local result alias.
- `Error::request` boxes an `errorpb::Error` as `Error::Request`.
- `Error::has_region_error` matches nested storage/transaction/MVCC request errors and direct `Error::Request`.
- `extract_region_error` unwraps nested request errors into `errorpb::Error`; non-region errors become a generic message-bearing `errorpb::Error`.
- `into_error_event` maps errors into `cdcpb::Error`: sink congestion and memory quota become `Congested`; `not_leader` and `epoch_not_match` pass through; all other cases currently map to `region_not_found`.

## Control Flow

Most CDC functions use `?` into this `Error` type. When a failure must be sent to a downstream, callers invoke `into_error_event(region_id)`. Congestion-like local failures are represented as protocol `Congested` so clients can treat them as backpressure. Real raftstore region errors preserve their specific `not_leader` or `epoch_not_match` fields. For errors not represented in the CDC protocol, the fallback is `region_not_found`, with a TODO noting that the protocol should support more CDC-specific errors.

`has_region_error` is used by initializer deregistration policy: region errors, or failures while building a shared resolver, tear down the whole delegate; other errors can remove only the failing downstream.

## State And Persistence Behavior

The file has no mutable state and no persistence. It defines conversions and pure classification/mapping behavior.

## Dependencies And Integration Points

- TiKV storage errors from `tikv::storage::{kv,mvcc,txn}`.
- `engine_traits::Error`, `txn_types::Error`, and `std::io::Error`.
- CDC channel `SendError` for disconnected/full/congested sink cases.
- `tikv_util::memory::MemoryQuotaExceeded`.
- Protobuf error types from `kvproto::{cdcpb,errorpb}`.
- `thiserror` for display/source implementations.

## Risks And Edge Cases

- The fallback from unknown errors to `region_not_found` can hide the real error class from clients. This is explicitly marked as incomplete protocol coverage.
- `has_region_error` relies on exact nested box-pattern matching. If TiKV storage error wrapping changes, region errors may be misclassified and cause downstream-only deregistration instead of delegate teardown.
- Congestion and memory-quota errors are collapsed into the same CDC `Congested` event, which is useful for retry/backpressure but loses detail.
- `extract_region_error` consumes `self`; callers must not expect to inspect the original error afterwards.

## Test Signals

There are no tests in this file, but delegate and endpoint tests exercise `into_error_event` indirectly for `not_leader`, `epoch_not_match`, congestion, generic errors mapping to `region_not_found`, and admin split/merge error conversion. Direct unit tests for nested storage error variants would make `has_region_error` safer against future error type changes.
