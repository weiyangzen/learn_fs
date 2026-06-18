# sources/storage-engines/rocksdb/utilities/transactions/transaction_util.cc

## Purpose
This implementation provides RocksDB transaction conflict-checking helpers. It determines whether keys read or locked by a transaction have been changed since a sequence-number snapshot and, when user-defined timestamps are enabled, whether newer timestamped versions conflict with a transaction validation timestamp.

## Important APIs, Types, and Functions
`TransactionUtil::CheckKeyForConflicts()` is the public single-key entry point. It casts the public column-family handle to `ColumnFamilyHandleImpl`, obtains the `ColumnFamilyData`, refs the current `SuperVersion`, gets the earliest maintained memtable sequence number, delegates to `CheckKey()`, and returns the `SuperVersion`.

`TransactionUtil::CheckKey()` performs the actual conflict check. It accepts `DBImpl`, a referenced `SuperVersion`, `earliest_seq`, the transaction snapshot sequence `snap_seq`, a key, optional read timestamp, `cache_only`, optional `ReadCallback` snapshot checker, optional `min_uncommitted`, and the `enable_udt_validation` toggle. It decides whether memtable history is sufficient or whether SST lookup is needed, calls `DBImpl::GetLatestSequenceForKey()`, interprets sequence visibility through either simple `snap_seq < seq` logic or `snap_checker->IsVisible(seq)`, and optionally compares stored and read timestamps with the column-family user comparator.

`TransactionUtil::CheckKeysForConflicts()` iterates a `LockTracker` by column family and key. For each tracked point lock, it retrieves the saved lock sequence and calls `CheckKey()` with no timestamp validation. The comments note this path is currently used by optimistic transactions and still lacks timestamp-based conflict checking.

## Control Flow
The single-key flow is: validate/ref column family `SuperVersion`, compute earliest memtable sequence, call `CheckKey()`, cleanup `SuperVersion`, return status. Inside `CheckKey()`, an unknown earliest sequence or a memtable history newer than the snapshot forces `need_to_read_sst`. If `cache_only` is true in those cases, the function returns `TryAgain` instead of reading SSTs. Otherwise, it queries the latest version for the key with either memtable-only or memtable-plus-SST lookup. Non-OK, non-NotFound, non-MergeInProgress statuses propagate. If a record is found, a sequence conflict is detected via snapshot ordering or the supplied read callback. If that does not already conflict and timestamp validation is enabled, the stored timestamp is compared against the transaction read timestamp; a DB timestamp greater than the read timestamp returns `Status::Busy()`.

The multi-key flow creates a column-family iterator from `LockTracker`, refs each `SuperVersion`, creates a key iterator for that column family, checks every key's tracked sequence, breaks on the first error or conflict, returns the `SuperVersion`, and then proceeds or exits.

## State and Persistence Behavior
This file does not mutate durable DB state. It reads transient in-memory DB state through `SuperVersion`, memtables, and optionally SST files. `cache_only` controls whether it may consult SST files; when the retained memtable history is insufficient and cache-only mode is requested, it refuses with `TryAgain` so callers do not silently validate with incomplete history. User-defined timestamp checks depend on timestamps stored with keys and comparator timestamp semantics.

## Dependencies and Integration Points
The implementation depends on `DBImpl::GetAndRefSuperVersion()`, `ReturnAndCleanupSuperVersion()`, `GetEarliestMemTableSequenceNumber()`, and `GetLatestSequenceForKey()`, plus `ColumnFamilyHandleImpl`, `ColumnFamilyData`, `ReadCallback`, `LockTracker`, `PointLockStatus`, and comparator timestamp APIs. It is integrated with pessimistic transaction validation, optimistic transaction conflict checks, write-prepared/non-ordered commit visibility through `ReadCallback`, and timestamp validation tested by `write_committed_transaction_ts_test.cc`.

## Risks and Edge Cases
Incorrect `SuperVersion` cleanup would leak refs, so every successful ref must be returned. If `earliest_seq` is unknown or too new, cache-only callers can see `TryAgain` instead of a definitive conflict result. Timestamp validation assumes `read_ts` and the latest key timestamp match the comparator timestamp size; assertions catch misuse in debug builds. The lower-bound logic differs when `min_uncommitted` is supplied, so callers must provide a valid `snap_checker` in non-ordered commit modes. `CheckKeysForConflicts()` does not yet check timestamps, which is a known limitation for optimistic transactions.

## Test Signals
Direct signals include timestamp validation tests that check `GetForUpdate()` conflict behavior, tombstone timestamp conflicts, and disabled UDT validation. Broader transaction tests exercise sequence-number conflict detection, insufficient memtable-history `TryAgain`, multi-key lock tracker validation, and `ReadCallback` visibility under write-prepared or unordered commit modes.
