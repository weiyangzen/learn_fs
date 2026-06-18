# sources/storage-engines/tikv/components/backup-stream/src/metadata/store/mod.rs

## Purpose
`metadata/store/mod.rs` defines the generic metadata storage abstraction used by `MetadataClient`, plus transaction, key selection, revision, watch, and snapshot data structures. It also exposes the PD-backed and in-memory test store implementations.

## Important APIs, types, and functions
- `Transaction`, `TransactionOp`, and `PutOption` model write batches with put/delete operations.
- `Condition` and `CondTransaction` model compare-and-branch transactions.
- `WithRevision<T>` attaches a metadata revision to snapshot results and supports `map`.
- `Keys` selects exact keys, prefixes, or ranges and converts them into half-open byte bounds.
- `GetExtra` and `GetResponse` support descending order, limits, historical revision hints, and pagination flags.
- `Snapshot` provides `get_extra`, `revision`, and default `get`.
- `KvEvent`, `KvEventType`, `Subscription`, and `KvChangeSubscription` model cancelable watch streams.
- `MetaStore` defines `snapshot`, `watch`, `txn`, `txn_cond`, plus default `set`, `delete`, and `get_latest`.

## Control flow
High-level clients request `get_latest`, which obtains a snapshot then reads keys from it, preserving the snapshot revision for later watches. Watches return streams plus a lazy cancel future. Default `set` and `delete` lower to `txn`.

## State and persistence behavior
The abstraction itself holds no data. It defines the semantics concrete stores must provide: consistent snapshots, revisioned reads, watch streams from a revision, and atomic or conditional writes.

## Dependencies and integration points
It uses `async_trait`, `tokio_stream::Stream`, and the metadata key wrappers. `PdStore` and `SlashEtcStore` implement this trait; `MetadataClient` is generic over it.

## Risks and edge cases
- Not all concrete stores implement all trait methods meaningfully; `PdStore` returns unsupported errors for generic transactions.
- `GetExtra.rev` is defined but not honored by the visible store implementations in this subset.
- `Keys::Key` uses `key.next()` by appending a zero byte, relying on byte-range ordering to isolate one exact key.

## Test signals
No direct tests in this module. It is covered through PD store tests, SlashEtc-backed metadata tests, and client tests.
