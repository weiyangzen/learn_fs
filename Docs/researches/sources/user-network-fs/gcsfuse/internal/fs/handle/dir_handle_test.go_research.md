<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle_test.go

## Purpose

This ogletest suite validates `DirHandle` listing behavior against a fake GCS bucket and real `inode.DirInode` instances. It focuses on merged local/GCS entries, conflict resolution, entry core fetching, and `ReadDirPlus` plus-entry handling.

## Important APIs, Types, and Functions

`DirHandleTest` owns a context, simulated clock, syncer bucket, and handle. `resetDirHandle` builds a `NewDirInode` for `testDir` and a `NewDirHandle`. Helper methods validate plain dirents, build `DirentPlus` values, validate plus entries, and validate file `Core` results.

Test methods include `EnsureEntriesWithLocalAndGCSFiles`, `EnsureEntriesWithSameNameLocalAndGCSFile`, `EnsureEntriesWithSameNameLocalFileAndGCSDirectory`, `ReadAllEntryCoresReturnsAllEntryCores`, `FetchEntryCoresFetchesCores`, `FetchEntryCoresNonZeroOffsetNoFetchIfCacheValid`, `ReadDirPlusSameNameLocalAndGCSFile`, and `ReadDirPlusSameNameLocalFileAndGCSDirectory`.

## Control Flow

Tests seed fake GCS objects under `testDir`, pass synthetic local-file maps, call unexported helpers or public handle methods, and inspect `dh.entries`, `dh.entriesPlus`, returned cores, and offsets. The `ReadDirPlus` tests pass prebuilt plus entries rather than relying on kernel lookup paths.

## State and Persistence Behavior

State is held in the simulated fake bucket and in the `DirHandle` cache fields. Each test starts from a reset handle and simulated clock. No persistent files are written.

## Dependencies and Integration Points

The suite exercises `handle.DirHandle` with `inode.NewDirInode`, `gcsx.NewSyncerBucket`, `fake.NewFakeBucket`, `storageutil.CreateObject`, FUSE dirent types, metadata type classification, and `semaphore.NewWeighted` for inode construction.

## Risks and Edge Cases

The tests inspect internal slices directly, so they are sensitive to sorting order and offset assignment. They cover same-name local/GCS duplicate suppression and directory/file conflict suffixing, but they do not exhaustively test pagination or buffer truncation behavior in `ReadDir`.

## Test Signals

Signals include entry counts, entry names/types, file core names and min object names, plus-cache invalidation behavior, and consecutive offsets for conflict-resolved `DirentPlus` entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle_test.go -->
