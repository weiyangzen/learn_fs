# sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_readphase.rs

## Purpose
`resolve_lock_readphase.rs` implements the read/scanning phase for full lock resolution. It scans storage for locks whose start timestamps appear in a supplied transaction-status map, flattens normal and shared-lock records into individual `(Key, Lock)` pairs, and schedules `ResolveLock` as the write phase.

## Important APIs, types, and functions
The `ResolveLockReadPhase` command carries `HashMap<TimeStamp, TimeStamp>` and optional `scan_key`. It is a readonly `KvResolveLock` command. Its main API is `ReadCommand::process_read`, which returns either `ProcessResult::Res` or `ProcessResult::NextCommand { Command::ResolveLock }`. It uses shared `RESOLVE_LOCK_BATCH_SIZE`.

## Control flow
`process_read` builds an `MvccReader` in forward scan mode and calls `scan_locks_from_storage` with an optional lower bound and a filter that accepts locks whose `lock.ts` is in `txn_status`. For normal locks it pushes one `(key, lock)`. For `SharedLocks`, it iterates contained timestamps, filters again against `txn_status`, and pushes one pair per matching sub-lock using the same key. It records key-read histogram data using the flattened count.

If no matching pairs are found, the command returns `Res`. Otherwise it computes `next_scan_key` from the last flattened key when the scanner reports remaining data, and returns a `ResolveLock` command containing the flattened batch.

## State and persistence behavior
This phase is read-only and does not mutate MVCC state. It updates read statistics from `MvccReader` and records key-read histograms. Its state handoff is the flattened lock list and optional continuation key embedded in the write-phase command.

## Dependencies and integration points
It depends on `MvccReader::scan_locks_from_storage`, `tikv_util::Either` for normal versus shared locks, scheduler `ReadCommand`, and `ResolveLock`. It is the front half of the system-command flow described in `resolve_lock.rs`, and its continuation key determines whether lock resolution loops through the whole lock CF.

## Risks
Flattening a single shared-lock key into many pairs creates duplicate keys in one write batch. That is necessary to resolve sub-locks but can stress write-phase snapshot behavior. Large shared-lock records also create progress risk: if continuation always restarts at the same key without resolving enough sub-locks, the loop could repeat. The included tests specifically target this risk.

## Test signals
Tests verify that shared pessimistic locks are filtered by transaction status, that unrelated shared sub-locks are ignored, and that a single key with more than `RESOLVE_LOCK_BATCH_SIZE` sub-locks progresses through multiple read/write rounds without duplicate unresolved subsets and eventually unlocks the key.
