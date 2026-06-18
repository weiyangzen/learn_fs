# sources/sync-backup/syncthing/lib/model/folder_sendrecv.go

## Purpose
Implements the full send-receive puller: deciding needed work, creating/updating/deleting directories, files, and symlinks, reusing blocks, requesting remote blocks, finishing temp files, handling conflicts, batching DB updates, and tracking pull errors.

## Important APIs, Types, and Functions
Registers `newSendReceiveFolder` for `config.FolderTypeSendReceive`. Key types are `pullBlockState`, `copyBlocksState`, `dbUpdateType`, `dbUpdateJob`, `sendReceiveFolder`, and `FileError`. Major methods include `pull`, `pullerIteration`, `processNeeded`, `processDeletions`, `handleDir`, `checkParent`, `handleSymlink`, `deleteDir`, `deleteFileWithCurrent`, `renameFile`, `handleFile`, `reuseBlocks`, `copierRoutine`, `pullerRoutine`, `pullBlock`, `performFinish`, `finisherRoutine`, `dbUpdaterRoutine`, `pullScannerRoutine`, `moveForConflict`, `deleteDirOnDiskHandleChildren`, `scanIfItemChanged`, and `checkToBeDeleted`. Helpers include `blockDiff`, `populateOffsets`, `verifyBuffer`, `conflictName`, `isConflict`, and `existingConflicts`.

## Control Flow
`pull` runs up to three iterations until no changes or pull errors remain. Each `pullerIteration` starts DB updater, copier workers, a puller routine, and a finisher routine wired by channels. `processNeeded` classifies needed items: ignored/invalid entries become DB invalidations, deletions are deferred or executed, directories and symlinks are handled directly, files enter a job queue, and rename shortcuts are attempted by matching block hashes against pending deletions. File pulls build shared state, reuse temp blocks, reorder remaining blocks, copy from local/current/other-folder block indexes, request missing blocks from least-busy peers, then finish by setting metadata, replacing the target, and enqueueing DB updates.

## State and Persistence Behavior
Mutates filesystem contents through mkdir, chmod, xattrs/ownership, symlink creation, remove, rename/copy, versioner archive, temp file writes, sparse-file skips, and conflict-copy creation. Mutates DB through batched local updates, invalidations, deletions, block index reads, and local index events. In-memory state includes job queue, temp pull errors, global block stats, device activity, channels, wait groups, and per-file shared puller state.

## Dependencies and Integration Points
Integrates with model availability and `RequestGlobal`, `sharedPullerState`, job queue, scanner, protocol block/file metadata, fs/osutil operations, versioning, events, semaphores, config options, ignore matching, and database iterators. It is embedded by receive-only and receive-encrypted modes.

## Risks
This is high-risk synchronization code: channel ordering, context cancellation, partial temp files, DB batching, and filesystem race checks must align. Deletion logic intentionally refuses to remove changed or ignored content, but edge cases can cause repeated pull errors. Receive-encrypted skips hash verification locally. Some flush calls ignore return values. Global `blockStats` and `activity` couple work across folders.

## Test Signals
The listed subset has no direct send-receive test file, but block reorderer, device activity, fake connection, file batch, and receive-only tests cover important pieces. Additional tests should target rename shortcuts, conflict limits, directory delete error precedence, sparse zero blocks, receive-encrypted trailer shortcut, and cancellation paths.
