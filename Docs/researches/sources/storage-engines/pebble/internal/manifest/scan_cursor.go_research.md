# sources/storage-engines/pebble/internal/manifest/scan_cursor.go

## Purpose
`scan_cursor.go` models a resumable position for scanning the LSM by level and by file order, currently focused on finding external virtual tables after a cursor within user-key bounds.

## Important APIs, Types, And Functions
- `ScanCursor` stores `Level`, lower-bound `Key`, and tie-breaking `SeqNum`.
- `EndScanCursor`, `AtEnd`, `String`, and `Compare` provide cursor primitives.
- `MakeScanCursor` and `MakeScanCursorAfterFile` position at or immediately after a table.
- `FileIsAfterCursor` compares a file against a cursor.
- `NextExternalFile`, `NextExternalFileOnLevel`, and `FirstExternalFileInLevelIter` find the next external virtual table across L0 sublevels and L1+ levels.

## Control Flow
The scan orders files by level, then smallest user key, and for L0 ties by high sequence number. `NextExternalFile` searches the current level and advances to the next level when none is found. L0 searches all sublevel iterators and chooses the minimum cursor position; L1+ uses the level iterator directly. Candidate files must be virtual and backed by an external object according to the object provider.

## State And Persistence Behavior
The cursor is lightweight resumable in-memory state. It references persisted table metadata indirectly through `Version`, but the cursor itself is not encoded in the manifest.

## Dependencies And Integration Points
It depends on `base.Compare`, `base.UserKeyBounds`, `objstorage.Provider`, `objstorage.IsExternalTable`, `Version.Levels`, `Version.L0SublevelFiles`, and `LevelIterator.SeekGE`.

## Risks And Test Signals
Risks include off-by-one advancement after a file, L0 tie ordering, end-bound trimming, and behavior when the cursor is already at end. `scan_cursor_test.go` covers datadriven external-file iteration and checks idempotence before advancing the cursor.
