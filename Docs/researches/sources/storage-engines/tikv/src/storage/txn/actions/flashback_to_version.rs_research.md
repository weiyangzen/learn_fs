# sources/storage-engines/tikv/src/storage/txn/actions/flashback_to_version.rs

## Purpose
Implements the low-level actions for flashback-to-version over a key range. Flashback rolls back current locks, writes synthetic MVCC versions that restore each key to a target `flashback_version`, and uses a special prewrite/commit key to make the operation resumable and detectable.

## Important APIs, types, and functions
- `FLASHBACK_BATCH_SIZE` is `257`, reserving one slot for the next-key cursor across batches.
- `flashback_to_version_read_lock` scans lock CF, skipping the flashback transaction's own prewrite lock.
- `rollback_locks` rolls back exclusive and shared locks using `rollback_lock`/`rollback_shared_lock`.
- `flashback_to_version_read_write` scans latest user keys in write CF and returns keys needing restoration.
- `flashback_to_version_write` writes synthetic `Put` or `Delete` write records at `flashback_commit_ts`, using `flashback_start_ts` as the start timestamp.
- `prewrite_flashback_key`, `commit_flashback_key`, `check_flashback_commit`, and `get_first_user_key` manage the special marker key.

## Control flow
The read-lock phase scans `[next_lock_key, end_key)` and filters out locks at `flashback_start_ts`, allowing retries after the flashback marker lock has been written. `rollback_locks` iterates the collected locks until `MAX_TXN_WRITE_SIZE`, setting `reader.start_ts` to each lock's timestamp before calling normal rollback logic. For shared locks it snapshots timestamps, rolls each sub-lock back, and updates the local `SharedLocks` value between iterations.

The write phase scans latest committed user keys and filters out the prewrite marker key, keys whose latest version is already at or before `flashback_version`, and keys already written at `flashback_commit_ts`. For every key, it fetches the visible write at `flashback_version`; a visible long put also copies default CF data to `flashback_start_ts`, while a missing visible write becomes a `WriteType::Delete`.

The marker-key prewrite picks the first user key that needs flashback, writes a lock representing the old value at the target version, and is idempotent if the lock or copied long value already exists. Commit converts that marker lock into a write and unlocks it. `check_flashback_commit` returns false for the expected live marker lock, true for the expected committed marker write, and `FlashbackNotPrepared(region_id)` for mismatched state.

## State and persistence behavior
Flashback mutates lock CF by rolling back locks and by writing/removing the marker lock. It mutates write CF with rollback records for old locks, synthetic versions for restored keys, and the marker commit record. It mutates default CF only when restoring long values. Batches stop early with `Some(next_key)` if `txn.write_size() >= MAX_TXN_WRITE_SIZE`.

## Dependencies and integration points
The module integrates with `MvccReader`, `SnapshotReader`, `MvccTxn`, `check_txn_status::{rollback_lock, rollback_shared_lock}`, `txn_types::{Lock, SharedLocks, Write}`, and command-layer flashback phases. It relies on range scans over lock/write CF and normal MVCC read helpers for value lookup.

## Risks and edge cases
Flashback assumes no writes commit after flashback begins; `flashback_to_version_read_write` asserts latest commit timestamps are not beyond `flashback_commit_ts`. Retry safety depends on skipping already flashed-back keys and on marker-key idempotence. Shared lock rollback must preserve/update local state as sub-locks are removed. Long-value copying must avoid duplicate default CF writes while still restoring data for non-short values.

## Test signals
Tests cover restoring across put/delete/rollback/lock histories, deleted keys, pessimistic locks, duplicate flashback writes, duplicate marker prewrite, start/end-key marker selection including last-region `None` end key, marker commit, and rolling back multiple shared pessimistic locks before writing restored versions.
