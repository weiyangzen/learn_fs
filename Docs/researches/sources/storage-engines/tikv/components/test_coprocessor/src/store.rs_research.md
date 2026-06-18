# sources/storage-engines/tikv/components/test_coprocessor/src/store.rs

## Purpose
This file implements a small transactional MVCC store wrapper for coprocessor tests. It can insert/delete table rows and indexes, commit them through `SyncTestStorageApiV1`, export committed data, and convert committed state into `SnapshotStore` or `FixtureStore`.

## Important APIs, Types, And Functions
`Insert<'a, E>` accumulates per-column legacy `Datum` values and row-v2 `ScalarValue`s. `execute_with_ctx` encodes a row key/value, prepares secondary index KVs, and prewrites them. `execute_with_v2_checksum` writes row codec v2 data, optionally with checksum. `Delete<'a, E>` computes row and index keys for a row and prewrites deletes.

`Store<E>` wraps `SyncTestStorageApiV1`, current and last committed timestamps, buffered handles to commit, and an optional PD client for TSO allocation. `begin` chooses a timestamp, `put` and `delete` prewrite mutations, `commit_with_ctx` commits all buffered handles, `export` scans committed data, `to_snapshot_store` and `to_fixture_store` expose committed views, and `insert_all_null_row` creates a row-v2 null row. `ToTxnStore` uses specialization to convert `Store` into concrete storage backends.

## Control Flow And State
All writes are two-phase: `begin` establishes `current_ts`, insert/delete prewrite mutations and record raw handles, then `commit` drains handles and updates `last_committed_ts`. Without a PD client, timestamps come from the crate's atomic `next_id`; with a PD client, `get_tso` is awaited with a five-second timeout.

## Persistence And Integration Points
The persisted state is the underlying test engine's MVCC data. Integration points include TiDB row/table codecs, `txn_types::Mutation`, `SnapshotStore`, `FixtureStore`, `GcConfig`, and the `test_storage` synchronous API.

## Risks And Test Signals
`put` assumes at least one KV and uses the first as primary. `delete` deduplicates only adjacent equal keys, so callers should pass stable rows if duplicates matter. `export` is capped at 100,000 records. The unit test `test_export` verifies commit visibility, delete behavior, ordering, duplicate deletes, and uncommitted data isolation.
