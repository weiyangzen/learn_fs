# sources/storage-engines/tikv/components/backup/src/errors.rs

## Purpose
This module defines the backup crate’s error type and conversion into BR protobuf errors. It centralizes how storage, transaction, region, IO, semaphore, codec, and cluster-id failures become client-visible `brpb::Error` values and backup error metrics.

## Important APIs, Types, And Functions
`Error` is a `thiserror` enum with variants for boxed generic errors, RocksDB string errors, IO, TiKV KV errors, engine-traits errors, transaction errors, cluster-id mismatch, invalid CF, semaphore acquire failure, closed channel, and codec errors. `impl From<Error> for ErrorPb` converts structured backup errors to protobuf response errors. `impl_from!` maps `String` into `Rocks`, and `From<async_channel::SendError<T>>` maps send failure to `ChannelClosed`. `Result<T>` aliases `std::result::Result<T, Error>`.

## Control Flow
The protobuf conversion pattern-matches nested TiKV error enums. Region request errors are recognized through nested `KvError`, `TxnError`, and `MvccError` wrappers and passed through as `region_error`, while metrics label the exact region failure kind when known. `KeyIsLocked` becomes a `kvrpcpb::KeyError`. KV timeouts become `ServerIsBusy` region errors with a message. Cluster-id mismatch fills `cluster_id_error`. Unknown cases become string messages.

## State And Persistence Behavior
The module has no durable state. It mutates Prometheus counters in `BACKUP_RANGE_ERROR_VEC` while converting errors, so error serialization has a metric side effect. That coupling means repeated conversions of the same error would increment counters repeatedly.

## Dependencies And Integration Points
It depends on `kvproto` BR/error/KV protobufs, TiKV storage KV/MVCC/transaction error internals, `engine_traits::Error`, `tikv_util::codec::Error`, Tokio semaphore acquire errors, `thiserror`, and crate metrics. It is consumed by endpoint and disk/save flows when setting `BackupResponse.error`.

## Risks And Edge Cases
The matching relies on nested boxed error shapes and the crate-level `box_patterns` feature. New TiKV error variants may fall into the generic `other` branch until explicitly handled, reducing retry precision. Timeout handling only matches `Error::Kv` timeouts, not every possible nested transaction timeout. Metric increments during conversion are useful but can make tests or callers sensitive to conversion count.

## Test Signals
There are no inline tests in this file, though a TODO notes error conversion testing. Endpoint tests exercise key-is-locked, not-leader, and timeout-to-server-is-busy conversion paths.
