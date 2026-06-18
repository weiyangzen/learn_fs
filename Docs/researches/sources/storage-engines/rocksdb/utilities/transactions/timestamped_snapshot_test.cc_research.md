# sources/storage-engines/rocksdb/utilities/transactions/timestamped_snapshot_test.cc

## Purpose

This file tests timestamped snapshot creation, lookup, ordering, release, and close behavior for transaction DBs. It focuses on write-committed support and sanity-checks unsupported write-prepared/write-unprepared configurations.

## Important APIs, Types, And Functions

- `TimestampedSnapshotWithTsSanityCheck` is instantiated for unsupported write policies.
- `TransactionTest` is instantiated for write-committed combinations of stackable DB, two-write-queue, per-key lock manager, and deadlock timeout.
- `TsCheckingTxnNotifier` implements `TransactionNotifier::SnapshotCreated()` and asserts nondecreasing snapshot sequence and timestamp order.
- Tests use `CommitAndTryCreateSnapshot`, `Prepare`, `Rollback`, transaction reuse via `BeginTransaction(..., old_txn)`, `CreateTimestampedSnapshot`, exact/latest/all/range snapshot lookups, `ReleaseTimestampedSnapshotsOlderThan`, and `Close`.

## Control Flow

Unsupported-policy tests expect `InvalidArgument` when no commit timestamp is provided and `NotSupported` when an explicit commit timestamp is requested. Write-committed tests then validate missing timestamp rejection, transaction-object reuse after snapshot-creating commits, commit-time snapshot creation after prepare, explicit DB snapshot creation, ordering constraints, close failure with outstanding snapshots, and multiple-snapshot range/release behavior.

`SequenceAndTsOrder` captures the key invariant: snapshot timestamps must not move backward; equal timestamp reuse is allowed only at the same sequence; larger timestamps can create new snapshots at the same sequence; equal or smaller timestamps at higher sequence fail to create a snapshot even if commit succeeds.

## State And Persistence Behavior

Timestamped snapshots are `shared_ptr<const Snapshot>` objects carrying sequence number and transaction timestamp. DB lookup structures can release older snapshots while application-held shared pointers remain valid. Outstanding DB-owned timestamped snapshots can make `Close()` return `Aborted`.

Commit-time snapshots are created after successful transaction persistence and are retrievable from both the transaction and DB snapshot lookup APIs.

## Dependencies And Integration Points

The tests depend on `transaction_test.h`, transaction DB parameterization, `TransactionNotifier`, `ManagedSnapshot`, `DBImpl::seq_per_batch()`, and public timestamped snapshot APIs.

## Risks And Test Signals

Risks include sentinel timestamp misuse, monotonic timestamp/sequence ordering, unsupported policy behavior, snapshot lifetime leaks blocking close, and notifier order assumptions. This file is the direct regression suite for those behaviors.
