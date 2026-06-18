# sources/user-network-fs/rclone/fs/sync/sync.go

## Purpose
This file is the core implementation of rclone directory sync, copy, move, and in-place transform operations. It coordinates listing/marching, checking, transfer queues, deletion modes, rename tracking, directory metadata/modtime handling, backup/compare/copy destinations, error aggregation, and duration cutoffs.

## Important APIs, Types, and Functions
- `syncCopyMove` is the central operation state object, storing source/destination filesystems, config/filter state, queues, maps, wait groups, error fields, rename tracking, backup/copy-dest state, directory metadata state, and overlap policy.
- Public entry points: `Sync`, `CopyDir`, `MoveDir`, and `Transform`.
- Internal orchestration: `newSyncCopyMove`, `runSyncCopyMove`, and `(*syncCopyMove).run`.
- Pipeline workers: `pairChecker`, `pairRenamer`, `pairCopyOrMove`, plus `start/stopCheckers`, `start/stopTransfers`, `start/stopRenamers`, `start/stopTrackRenames`, and `start/stopDeleters`.
- March callbacks: `SrcOnly`, `DstOnly`, and `Match`.
- Rename helpers: `parseTrackRenamesStrategy`, `renameID`, `makeRenameMap`, `tryRename`, `pushRenameMap`, and `popRenameMap`.
- Directory helpers: `markParentNotEmpty`, `markDirModified`, `copyDirMetadata`, `setDelayedDirModTimes`, and `deleteEmptyDirectories`.
- Error helpers: `processError`, `currentError`, and `aborting`.

## Control Flow
`runSyncCopyMove` validates incompatible delete/move combinations and runs a delete-only pass for `DeleteModeBefore`. `newSyncCopyMove` snapshots global config/filter settings, validates overlap and option combinations, creates checker/transfer/rename pipes, configures max-duration contexts, resolves backup/copy destinations, and disables unsupported track-renames modes. `run` starts worker goroutines, runs `march.March` over source and destination, optionally builds a rename map from remaining destination files, drains queues, applies delete-after and directory cleanup/modtime updates, processes context/deadline errors, cancels contexts, and returns the highest-priority error.

## State and Persistence
Runtime state is held in maps/channels/slices on `syncCopyMove`: destination/source file maps, empty-directory maps, rename candidates, delayed directory modtimes, modified directories, and queued object pairs. Persistent effects occur on the source/destination/backup filesystems: object copies, moves, deletes, directory creation, metadata updates, and backup-dir moves.

## Dependencies and Integration Points
It integrates with `fs.ConfigInfo`, filters, accounting stats, `march`, `operations`, backend feature flags, hash/modtime support, logger options, error classification, transform path rewriting, and the `pipe` queue implementation. RC wrappers and CLI commands ultimately call these entry points.

## Risks and Edge Cases
This is high-risk destructive code. Incorrect option interactions can delete or move wrong objects, so overlap checks, `SkipDestructive`, delete modes, backup-dir handling, and auth/RC exposure matter. Concurrency spans multiple worker pools and maps protected by mutexes; queue close order and context cancellation are critical. Track-renames depends on hash/modtime/leaf strategies and destination maps, and may be disabled based on backend capabilities. Directory modtime updates are delayed and level-ordered to avoid parent/child timestamp churn. Max-duration handling differs between hard, soft, and graceful cutoff modes.

## Test Signals
This subset includes RC integration tests and pipe tests, but not the main sync engine's broader test suite. Existing signals here prove basic RC copy/move/sync outcomes and queue behavior; full confidence requires running the repository's sync/operations/fstest tests because this file touches destructive and backend-dependent behavior.
