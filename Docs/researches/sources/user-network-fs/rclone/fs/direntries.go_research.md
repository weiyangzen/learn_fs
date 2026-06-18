<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries.go -->
# sources/user-network-fs/rclone/fs/direntries.go

## Purpose
Defines helpers for slices of directory entries returned by list operations.

## Important APIs, Types, And Control Flow
`DirEntries` implements `sort.Interface` using `CompareDirEntries`. Iteration helpers run callbacks over only objects or only directories, with error-short-circuiting variants. `DirEntryType` classifies entries as object, directory, or unknown. `CompareDirEntries` sorts by remote path and then type, placing directories before objects for identical names because `directory` sorts before `object`.

## State And Persistence
Pure slice operations; no external state.

## Dependencies And Integration Points
Used by listing, operations, dirtree, and tests with mock objects/directories.

## Risks And Test Signals
Unknown entry types sort by formatted type string, which is mainly diagnostic. Tests cover stable sorting with duplicate object names and same-name directory/object pairs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries.go -->
