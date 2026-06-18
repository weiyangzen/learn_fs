# sources/storage-engines/rocksdb/utilities/transactions/snapshot_checker.cc

## Purpose

This file implements snapshot-membership helpers for transaction-aware RocksDB visibility. It adapts write-prepared transaction state to the `SnapshotChecker` interface and provides fast predicates for sequence-number visibility relative to a snapshot.

## Important APIs And Functions

- `WritePreparedSnapshotChecker::CheckInSnapshot()` calls `WritePreparedTxnDB::IsInSnapshot()` and maps the result to `kInSnapshot`, `kNotInSnapshot`, or `kSnapshotReleased`.
- `DisableGCSnapshotChecker::Instance()` returns a process-lifetime singleton using `STATIC_AVOID_DESTRUCTION`.
- `DataIsDefinitelyInSnapshot()` returns true when `seqno <= snapshot` and no checker contradicts membership.
- `DataIsDefinitelyNotInSnapshot()` returns true when `seqno > snapshot` or a checker explicitly reports not-in-snapshot.

## Control Flow

The write-prepared checker delegates the hard visibility decision to `WritePreparedTxnDB`, because sequence-number ordering alone is insufficient around prepared and committed transaction records. The free helper functions provide branch-predicted fast paths for callers that only need definitive answers.

## State And Persistence Behavior

No durable state is stored here. `WritePreparedSnapshotChecker` keeps a raw transaction DB pointer; the singleton checker has static process lifetime. Visibility state is maintained by the transaction DB and DB snapshot structures.

## Dependencies And Integration Points

The file depends on `db/snapshot_checker.h`, `port/lang.h`, and `write_prepared_txn_db.h`. It is used by transaction-aware read, compaction, GC, and conflict-checking code that must reason about snapshot visibility.

## Risks And Test Signals

The TODO around `min_uncommitted` is a risk if write-prepared visibility needs tighter bounds. Raw pointer lifetime must exceed checker use. Released snapshots are represented distinctly from not-in-snapshot. Coverage is indirect through write-prepared snapshot, compaction, and transaction visibility tests.
