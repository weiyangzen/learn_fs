# sources/storage-engines/tikv/src/storage/txn/actions/check_data_constraint.rs

## Purpose
This file implements the not-exists/existence constraint check used by prewrite and pessimistic lock acquisition. It decides whether a key already exists when a mutation requests `should_not_exist`.

## Important APIs, Types, and Functions
- `check_data_constraint` is the only production function. The caller must pass the latest write for the key.
- It returns `Ok(())` when no constraint applies, the latest write is a delete, or the latest put has a nonzero GC fence that makes it invalid as the latest visible version.
- It returns `ErrorInner::AlreadyExist` with the raw key and existing start timestamp when the key exists.

## Control Flow
The function first treats nonzero `gc_fence` as invalid latest data. If `should_not_exist` is false, or the latest write is `Delete`, or the write is invalidated by GC fence, it returns success. Otherwise a latest `Put` is immediate evidence of existence. For latest `Rollback` or `Lock`, it asks `SnapshotReader::get_write` for an older visible write before `write_commit_ts`; if one exists, the key exists.

## State and Persistence Behavior
The function is read-only. It may perform an additional write-CF lookup for older versions but does not mutate `MvccTxn` or engine state.

## Dependencies and Integration Points
It depends on `txn_types::{Key, TimeStamp, Write, WriteType}` and `SnapshotReader`. It is used by pessimistic lock acquisition and related prewrite paths to implement insert/not-exist assertions against MVCC history and GC fence semantics.

## Risks
Correctness depends on the caller's guarantee that `write` is the latest version. Passing an older write can allow duplicate inserts or false `AlreadyExist` errors. The GC-fence shortcut assumes nonzero fence means the latest data is logically deleted for this check.

## Test Signals
`test_check_data_constraint` covers skip cases, delete, latest put conflict, and older-version detection behind rollback/lock records. More coverage would be useful for GC-fence invalidation and real prewrite/acquire paths.
