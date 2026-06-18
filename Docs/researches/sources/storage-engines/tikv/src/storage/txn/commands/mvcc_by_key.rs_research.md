# sources/storage-engines/tikv/src/storage/txn/commands/mvcc_by_key.rs

## Purpose
Implements a readonly diagnostic command that returns MVCC lock, write, and value history for one key.

## Important APIs, Types, and Functions
`MvccByKey` has a single `key` field and returns `MvccInfo`. `CommandExt` marks it readonly, uses the `key_mvcc` metric tag, reports zero write bytes, and generates an empty latch. `process_read` calls `actions::mvcc::find_mvcc_infos_by_key`.

## Control Flow
The command creates an `MvccReader` without a scan mode, reads all MVCC information for the key, adds reader statistics to scheduler statistics, and returns `ProcessResult::MvccKey`.

## State and Persistence
No state is persisted and no latches are held. It only reads lock, write, and value data through the snapshot supplied by the scheduler.

## Dependencies and Integration Points
Constructed from `MvccGetByKeyRequest` in `mod.rs` and dispatched through `Command::process_read`. It depends on `MvccInfo` protobuf-facing storage types and shared MVCC diagnostic actions.

## Risks and Test Signals
Risks are mostly operational: large histories can produce heavy reads, and diagnostic callers need a consistent snapshot. Coverage is indirect through MVCC action tests and storage diagnostics.
