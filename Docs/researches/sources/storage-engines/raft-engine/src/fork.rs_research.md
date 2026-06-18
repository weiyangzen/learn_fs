# sources/storage-engines/raft-engine/src/fork.rs

## Purpose
`fork.rs` implements `Engine::fork` for `Engine<F, FilePipeLog<F>>`, creating a minimally copied clone of an unopened raft-engine directory. It lets source and target engines run independently afterward by symlinking immutable inactive files and copying each queue's active tail file.

## Important APIs, Types, And Functions
`CopyDetails` reports `copied` and `symlinked` destination paths. `Engine::fork` is the public method and delegates to `minimum_copy`. `minimum_copy` validates configuration, creates the target directory, scans source log files without locking, then iterates append and rewrite file lists.

For each queue, every file except the last is symlinked into the target using the queue filename built from `FileId`; the last file is copied. Paths recorded in `CopyDetails` are canonicalized destination paths.

## Control Flow
`minimum_copy` first rejects `enable_log_recycle = true`, because recycled file reuse could mutate files shared by symlink. It also rejects `RecoveryMode::TolerateAnyCorruption`, because that mode may rewrite or truncate shared symlinked files during recovery. It sanitizes a cloned config, creates the target directory, builds a `FilePipeLogBuilder`, and calls `scan_and_sort(false)` so it can discover files without taking directory locks.

The file iteration preserves queue order from the builder. If a queue has N files, files `[0..N-1)` are symlinked and file `N-1` is copied. The active copied tail gives each fork an independent append point while sharing stable history.

## State And Persistence Behavior
The function writes a new target directory containing symlinks and copies. It does not mutate source files. It assumes the source engine is not open; the doc comment warns that using an active source can corrupt data because the scan and copy are not coordinated with concurrent writes.

## Dependencies And Integration Points
It depends on `Config`, `RecoveryMode`, `FileSystem`, `FilePipeLogBuilder::scan_and_sort`, `FileNameExt`, `FileId`, and OS symlink APIs. The impl is specialized for `Engine<F, FilePipeLog<F>>`, so other `PipeLog` implementations do not receive this method.

## Risks And Edge Cases
The target must not already exist as conflicting files; `create_dir_all` permits an existing directory, so later symlink or copy calls fail if destination names exist. The source is scanned without locking, relying on the caller to ensure it is closed. Canonicalization unwraps after symlink/copy success and can panic if the destination cannot be canonicalized. On Windows it uses file symlinks, which may require privileges or developer mode.

## Test Signals
`test_fork` writes several key-value batches and rewrite cycles, forks the source, opens the target, verifies all pre-fork keys are visible, then verifies source and target can diverge independently. It also asserts rejection when log recycle is enabled or recovery mode is `TolerateAnyCorruption`.
