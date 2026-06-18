# sources/user-network-fs/rclone/fs/operations/operations.go

## Purpose
`operations.go` is the central generic operations module for rclone filesystems and objects. It implements equality checks, move/delete/list/hash/count/directory operations, stream uploads, URL copies, backup/compare/copy-dest support, transfer decisions, destructive-operation prompting, list formatting, directory metadata, and filesystem info extraction.

## Important APIs, types, and functions
- Equality and identity: `CheckHashes`, `Equal`, `DirsEqual`, `CommonHash`, `SameObject`, `SameRemoteType`, `SameConfig`, `Same`, `SameDir`, `OverlappingFilterCheck`, `NeedTransfer`.
- Move/copy/delete orchestration: `Move`, `MoveTransfer`, `DeleteFileWithBackupDir`, `DeleteFilesWithBackupDir`, `Purge`, `Delete`, `RemoveExisting`, `MoveFile`, `TransformFile`.
- Listing/output/hash utilities: `ListFn`, `List`, `ListLong`, `HashSum`, `HashLister`, `HashSumStream`, `Count`, `ListDir`, `SizeString`, `CountString`, and synchronized print helpers.
- Directory and metadata operations: `Mkdir`, `MkdirMetadata`, `MkdirModTime`, `TryRmdir`, `Rmdir`, `Rmdirs`, `DirMove`, `DirMoveCaseInsensitive`, `CopyDirMetadata`, `SetDirModTime`.
- Streaming and external input: `Cat`, `Rcat`, `RcatSize`, `CopyURL`, `CopyURLToWriter`.
- Policy/config helpers: `GetCompareDest`, `GetCopyDest`, `CompareOrCopyDest`, `BackupDir`, `MoveBackupDir`, `SkipDestructive`, `Retry`, `GetFsInfo`.
- Formatting: `ListFormat` and `FormatForLSFPrecision`.

## Control flow
Equality first compares size unless ignored, then respects size-only/checksum/mtime/update flags, reads common hashes when useful, may update destination modtime, and emits logger callbacks. `NeedTransfer` layers higher-level policy on top: destination absence, ignore-existing, ignore-times, update-older, custom equal functions, and same-object detection.

Move tries backend server-side move when configs/types allow it, deleting or case-renaming destinations safely, then falls back to copy plus source delete. Copy behavior is implemented in `copy.go`, while `moveOrCopyFile` coordinates object lookup, backup-dir/copy-dest/compare-dest, case-insensitive two-step moves, transfer decisions, and optional deletion of moved sources.

Listing and hash functions walk filesystems with `walk.ListR`, use checkers/transfers concurrency, and serialize output through `StdoutMutex`. Stream upload functions choose between small buffered `Put`, spooled temporary file `Put`, or backend `PutStream`, then verify the uploaded result through equality logic. Directory move attempts backend `DirMove` first, otherwise creates destination directories, moves files in parallel, and removes source directories bottom-up.

## State and persistence behavior
This file performs most remote mutations in the operations package: object creation/update/removal, server-side moves/copies, directory creation/removal, trash cleanup, backup moves, tier changes, touch operations, and metadata/modtime updates. It mutates accounting statistics and logger outputs. Interactive skip decisions are cached in the package-level `skipped` map protected by `interactiveMu`; `checksumWarning` and `modTimeUploadOnce` suppress repeated logs.

## Dependencies and integration points
It integrates with nearly all rclone core primitives: `fs` interfaces and feature flags, `accounting`, `cache`, config/filter/fserrors/fshttp/hash/object/walk packages, `atexit`, `errcount`, `pacer`, `random`, `readers`, `transform`, `errgroup`, and Unicode normalization. Other files in this subset call its helpers heavily: `check.go` uses hashes/size/retry/listing/output, `copy.go` uses common hash and move/copy policies, `logger.go` is invoked by equality/transfer decisions, and `lsjson.go` reuses depth logic.

## Risks and edge cases
This is high-blast-radius code. Risks include accidental destructive operations when dry-run/interactive checks are bypassed, same-object detection on case-insensitive or Unicode-normalizing filesystems, overlapping backup/compare/copy destinations, partial failures during fallback directory moves, stream uploads that must spool large inputs, hashless remotes under checksum mode, modtime update semantics requiring reupload or delete, and global config/logging state leaking across operations. Some functions use backend optional features and must preserve fallback behavior when unsupported.

## Test signals
This subset includes `operations_internal_test.go` for `sizeDiffers`, while many exported functions are exercised indirectly by `copy_test.go`, `check_test.go`, `dedupe_test.go`, `lsjson_test.go`, and `multithread_test.go`. Broader rclone integration tests outside this work item cover sync, move, delete, listing, and backend feature combinations.
