# sources/storage-engines/tikv/components/backup-stream/src/metadata/store/slash_etc.rs

## Purpose
`metadata/store/slash_etc.rs` implements an in-memory, revisioned metadata store used for tests and integration helpers. It emulates a small etcd-like key-value store with MVCC revisions, tombstones, range reads, watches, and conditional transactions.

## Important APIs, types, and functions
- `SlashEtc` holds a `BTreeMap<Key, Value>`, subscribers, current revision, and subscriber id allocator.
- `SlashEtcStore` is `Arc<Mutex<SlashEtc>>`.
- `Key(Vec<u8>, i64)` orders metadata keys by key bytes and revision.
- `Value` is either `Val(Vec<u8>)` or `Del` tombstone.
- `Snapshot for WithRevision<SlashEtcStore>` reads keys from a captured revision value, with optional descending order and limit.
- Internal `set` and `delete` allocate revisions, mutate MVCC entries, and send watch events.
- `MetaStore for SlashEtcStore` implements snapshots, watches, transactions, and conditional transactions.

## Control flow
Reads convert `Keys` to byte bounds, scan all matching MVCC entries, group by key, and return the latest non-tombstone value for each key. Writes allocate a new revision, notify overlapping subscribers, then insert a value or tombstone. `watch` first sends historical events with revision greater than or equal to `start_rev`, then registers a live subscriber whose cancel future removes it.

## State and persistence behavior
All state is in memory and process-local. Revisions are monotonic. Deletes create tombstones rather than removing old entries. Subscribers receive put/delete events for key ranges intersecting their watch bounds.

## Dependencies and integration points
This store implements the same `MetaStore` trait as PD store and is returned by `metadata/test.rs::test_meta_cli`. It depends on Tokio mutexes and mpsc channels.

## Risks and edge cases
- Snapshot reads store only the revision number but `get_key` reads current data rather than filtering by snapshot revision, so it is not a full historical MVCC snapshot.
- Pending historical watch events are sent while holding the mutex and can panic if more than channel capacity is pending.
- `txn_cond` compares `k.0.0` rather than the value bytes of the selected key, which may not match intended etcd compare semantics.
- Subscriber sends unwrap, so closed receivers can panic during set/delete.

## Test signals
This file has no local test module, but it is heavily exercised by `metadata/test.rs` for task/range/progress/watch behavior and by `metadata/client.rs` checkpoint parsing tests.
