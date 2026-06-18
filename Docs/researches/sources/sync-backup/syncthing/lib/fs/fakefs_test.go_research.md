# sources/sync-backup/syncthing/lib/fs/fakefs_test.go

## Purpose
Validates fakeFS behavior against expected filesystem semantics and, where possible, compares it with a real local filesystem of matching case sensitivity.

## Important APIs, Types, and Functions
`TestFakeFS`, `TestFakeFSCaseSensitive`, `TestFakeFSCaseInsensitive`, `testFakeFSRead`, `testFakeFSOpenFile`, `testFakeFSRemoveAll`, `testFakeFSRemove`, `testFakeFSRename`, `testFakeFSMkdir`, `testFakeFSSameFile`, `testReadWriteContent`, `createTestDir`, `runTests`, and `cleanup`.

## Control Flow
Tests create directories/files/symlinks, write/read/seek, mutate ownership, and assert metadata. Shared test suites run against fakeFS and sometimes real `BasicFilesystem`, depending on detected case sensitivity. Case-insensitive tests open, stat, create, rename, remove, and list using varied casing.

## State and Persistence Behavior
Most state is in fakeFS global roots; cleanup removes entries except `.stfolder`. Real temp directories are used to detect host case sensitivity and as comparison backends.

## Dependencies and Integration Points
Depends on `build`, `runtime`, `path/filepath`, and `NewFilesystem` behavior.

## Risks
Global fakeFS cache means root names must be unique to avoid cross-test leakage. Tests are broad but mostly single-threaded except casefs stress elsewhere.

## Test Signals
Strong coverage for fakeFS as a scanner/test backend: file data generation, explicit content storage, case-insensitive path resolution, name preservation, and mutation semantics.
