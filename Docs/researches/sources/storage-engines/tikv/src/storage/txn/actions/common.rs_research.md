# sources/storage-engines/tikv/src/storage/txn/actions/common.rs

## Purpose
Provides shared helpers for transactional actions, currently focused on `last_change` metadata calculation and idempotence after prewrite errors. The helpers let prewrite/commit preserve newer TiKV metadata while still handling older records that lack that metadata.

## Important APIs, types, and functions
- `next_last_change_info(key, write, start_ts, original_reader, commit_ts) -> Result<LastChange>` returns the next `LastChange` for a new lock/write derived from the current latest write.
- `check_committed_record_on_err(prewrite_result, txn, reader, key)` converts selected prewrite errors into a successful idempotent response if the same transaction is already committed.
- Uses `TxnCommitRecord`, `LastChange`, `OldValue`, `Write`, `WriteType`, `SnapshotReader`, and `MvccTxn`.

## Control flow
`next_last_change_info` treats `Put` and `Delete` as fresh data changes at `commit_ts`. For `Lock` and `Rollback`, it reuses existing `LastChange` if it is `Exist` or `NotExist`. When the field is `Unknown`, usually from older TiKV data, it creates a new `SnapshotReader`, seeks the visible write at `commit_ts`, merges the temporary reader statistics back into the original reader, and returns either `NotExist` or a found put timestamp with an estimated distance.

`check_committed_record_on_err` checks `reader.get_txn_commit_record(key)`. If it finds one non-rollback commit record for the transaction, it logs the idempotent condition, clears `txn` to discard staged mutations, and returns an empty per-key result plus the found commit timestamp. Other cases rethrow the original prewrite error.

## State and persistence behavior
`next_last_change_info` is read-only except for accumulating read statistics. `check_committed_record_on_err` can clear staged `MvccTxn` modifications, so callers must only use it when a committed record supersedes the current failed prewrite attempt.

## Dependencies and integration points
`prewrite.rs` uses `next_last_change_info` for lock `last_change` calculation and pessimistic amend. Command prewrite paths can use `check_committed_record_on_err` to make retries idempotent when the write has already committed.

## Risks and edge cases
The compatibility scan for `LastChange::Unknown` may be expensive on long version chains but is required for old data. Correctly adding temporary statistics back to the original reader matters for observability. The idempotence helper cannot prove a transaction committed if MVCC GC removed the commit record, so it intentionally returns the original error in that case.

## Test signals
Coverage is mainly through `prewrite.rs` tests that verify last-change calculation from put/delete/lock/rollback records and through higher-level prewrite command idempotence tests.
