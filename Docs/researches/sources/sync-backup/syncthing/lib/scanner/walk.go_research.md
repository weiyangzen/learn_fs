# sources/sync-backup/syncthing/lib/scanner/walk.go

## Purpose
Implements Syncthing's filesystem scanning pipeline: walk configured subtrees, ignore or normalize paths, generate `protocol.FileInfo` metadata for changed directories/files/symlinks, hash changed regular files, emit scan results, and report progress/metrics.

## Important APIs, Types, and Functions
`Config` carries folder ID, subpaths, ignore matcher, temp lifetime, current-file lookup, filesystem, permissions/normalization/hash/progress settings, local flags, modtime window, event logger, ownership/xattr settings, and xattr filter. `CurrentFiler`, `XattrFilter`, and `ScanResult` define scanner contracts. Public entry points are `Walk` and `WalkWithoutHashing`. Core methods are `newWalker`, `walk`, `walkWithoutHashing`, `scan`, `walkAndHashFiles`, `handleItem`, `walkRegular`, `walkDir`, `walkSymlink`, `normalizePath`, `applyNormalization`, `updateFileInfo`, `handleError`, `byteCounter`, `noCurrentFiler`, and `CreateFileInfo`.

## Control Flow
`Walk` starts a filesystem scan goroutine producing files to hash and either starts hashers directly or buffers files to calculate progress totals before hashing. `scan` walks `.` or configured subpaths, skipping subpaths below symlinks and reporting unexpected walk failures. The walk function handles cancellation, metrics, UTF-8 validation, temp-file cleanup, internal-file skipping, ignore matching, normalization, and ignored-parent reconciliation. `handleItem` dispatches symlinks, directories, regular files, and special files. Regular files are compared with current metadata ignoring blocks; changed files go to hashers. Directories and symlinks emit results immediately. `CreateFileInfo` builds platform-aware metadata and symlink targets.

## State and Persistence Behavior
Persistent effects include removing expired temporary files and optionally renaming files to normalized UTF-8 names. It reads filesystem metadata, symlink targets, ownership, and xattrs. In-memory state includes ignored-parent tracking, progress counters, byte EWMA, current-file comparisons, and emitted `ScanResult` values. File versions are updated by incrementing the local short ID, setting `ModifiedBy`, preserving previous block hashes, and merging platform data.

## Dependencies and Integration Points
Depends on `lib/fs`, `ignore.Matcher`, `events.Logger`, `osutil.TraversesSymlink`, Unicode normalization, build platform flags, protocol `FileInfo` and vector clocks, scanner metrics, and `blockqueue.go` hashers. It feeds the model/index pipeline with local file metadata and block hashes.

## Risks and Edge Cases
Path handling is security-sensitive: invalid UTF-8, normalization conflicts, ignored parents that contain included children, internal files, temporary files, and symlink traversal all need correct decisions. Auto-normalization renames user files and can fail midway, returning a temp path to avoid data loss. Current-file equivalence must ignore the right fields or scanner can miss changes or rescan unnecessarily. Hash worker count and progress buffering can affect memory use for very large scans. Windows symlinks are ignored, and executable bits are preserved from existing index entries on Windows.

## Test Signals
This subset includes helper fakes in `virtualfs_test.go`, but the main walk tests are outside the requested files. Indirect signals include block hashing tests, scanner metrics initialization, and higher-level folder scan tests that verify ignore behavior, normalization, symlinks, version updates, ownership/xattr collection, progress events, and changed-file hashing.
