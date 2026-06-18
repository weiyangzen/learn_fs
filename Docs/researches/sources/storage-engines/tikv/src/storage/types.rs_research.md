# sources/storage-engines/tikv/src/storage/types.rs

## Purpose
`types.rs` defines shared storage-layer result and callback value types used by TiKV's MVCC, transaction, lock-manager, and raw APIs. It is a contract bridge between internal transaction processing results and protobuf-facing RPC responses.

## Important APIs, Types, and Functions
`MvccInfo` stores a key's optional lock, write records, and value records, with `into_proto` converting internal `Lock`, `Write`, `LastChange`, and timestamp fields into `kvrpcpb::MvccInfo`. `TxnStatus` represents primary-lock status outcomes such as rolled back, TTL expired, lock missing, uncommitted with pushed min-commit-ts signal, committed, pessimistic rollback, and do-nothing lock absence. `PrewriteResult`, `PessimisticLockParameters`, `PessimisticLockKeyResult`, `PessimisticLockResults`, and `SecondaryLocksStatus` carry transaction command results. The `storage_callback!` macro defines `StorageCallback` variants and maps `ProcessResult` variants into typed callback payloads.

## Control Flow
Storage commands produce `ProcessResult`; `StorageCallback::execute` matches the expected variant and calls the saved `Callback<T>` with either a typed success value or the shared error. Pessimistic lock results aggregate per-key outcomes, can be converted to protobuf tuples with a first shared error, and can also be converted into legacy `(values, not_founds)` vectors for older response shapes.

## State and Persistence Behavior
The file defines transient value objects. It does not persist data directly, but its conversions expose persisted MVCC metadata such as write type, start/commit timestamps, short values, GC fences, overlapped rollback flags, and last-change hints to clients.

## Dependencies and Integration Points
It depends on `kvproto::kvrpcpb`, `txn_types`, storage `Lock`, `Write`, `WriteType`, `WaitTimeout`, `SharedError`, and `txn::ProcessResult`. It is used throughout TiKV storage RPC handling as the common callback/result language.

## Risks and Test Signals
The main risk is mismatching a callback with the wrong `ProcessResult`, which intentionally panics. `PessimisticLockResults::into_legacy_values_and_not_founds` assumes all entries share the same response shape. Conversion logic must track protobuf field evolution, especially last-change and lock result fields. Local test helpers assert exact pessimistic lock result shapes.
