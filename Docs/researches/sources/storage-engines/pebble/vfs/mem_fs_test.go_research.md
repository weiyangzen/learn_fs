<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs_test.go -->
# sources/storage-engines/pebble/vfs/mem_fs_test.go

## Purpose
Tests MemFS behavior through datadriven scenarios, crash-clone equivalence, standalone memory files, concurrency around crash cloning, and MemFS lock semantics.

## Important APIs, Types, and Functions
`runMemFSDataDriven` interprets commands for file and filesystem operations. `checkClonedIsEquivalent` checks `Clone` round trips. `TestMemFSBasics`, `TestMemFSList`, `TestMemFSCrashable`, `TestMemFile`, `TestMemFSCrashCloneConcurrency`, and `TestMemFSLock` are the main test entry points.

## Control Flow
Datadriven commands create/open/link/rename/reuse/remove files, write/read/sync/close handles, list directories, crash-clone filesystems, and switch active FS handles. After each datadriven run, the test clones the filesystem through `Clone` using both empty and slash root paths and compares string dumps. The concurrency test runs crash cloning alongside reuse, link, and lock workers for a fixed duration. The lock datadriven test manages multiple named MemFS instances and lock handles.

## State and Persistence Behavior
Tests exercise synced versus unsynced state in `NewCrashableMem`, including random retention of unsynced data. The concurrency test stresses `cloneMu` ordering to catch deadlocks from recursive read locks when a crash clone is waiting. Lock tests validate per-MemFS lock maps and close-based release.

## Dependencies and Integration Points
Covers `mem_fs.go`, `Clone`, the VFS `File` interface, datadriven fixtures, and test randomness from `math/rand/v2`. These tests protect behavior used by broader Pebble DB and WAL tests.

## Risks and Edge Cases
The fixed five-second concurrency test is heavier than typical unit tests and may be sensitive to slow CI, but it targets a real deadlock class. The datadriven `f.readat` command appears to reuse the first command argument for both byte count and offset, limiting offset coverage.

## Test Signals
Passing demonstrates MemFS compatibility with the VFS contract, crashable sync modeling, root clone behavior, lock isolation, and absence of the known crash-clone deadlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs_test.go -->
