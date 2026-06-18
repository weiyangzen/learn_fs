<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_dir_test.go

## Purpose

This file tests directory listing behavior when local unsynced files, synced GCS files, explicit directories, unlinked files, and concurrent local creations coexist on a gcsfuse mount.

## Important APIs, Types, and Functions

Helpers `creatingNLocalFilesShouldNotThrowError` and `readingDirNTimesShouldNotThrowError` drive concurrent creation/listing. Tests use `os.ReadDir`, `filepath.WalkDir`, local file creation helpers, `operations.ReadDirectory`, `VerifyFileEntry`, `VerifyDirectoryEntry`, and `VerifyCountOfDirectoryEntries`.

## Control Flow

`TestReadDir` builds a mixed directory with an explicit dir containing a local file, empty local file, non-empty local file, and GCS-backed file, then validates listing sizes and types before closing local handles. `TestRecursiveListingWithLocalFiles` walks nested directories and validates local entries. `TestReadDirWithSameNameLocalAndGCSFile` creates a local file then a same-name GCS object and expects close ESTALE after listing. `TestConcurrentReadDirAndCreationOfLocalFiles_DoesNotThrowError` races 100 local file creations against 200 root listings. `TestStatLocalFileAfterRecreatingItWithSameName` validates stat after remove/recreate.

## State and Persistence Behavior

The tests exercise directory entry merging between local unsynced inode state and remote GCS object listings. Unclosed local files appear in listings with local sizes; close persists them or returns ESTALE when a remote conflict exists.

## Dependencies and Integration Points

It depends on local-file globals/helpers plus shared operations/client constants such as `ExplicitDirName`, `FileName1`, and size constants. It exercises the list/stat surfaces used by recursive filesystem clients.

## Risks and Test Signals

Directory entry order is assumed in several assertions. Concurrent test failures would signal locking/race problems. Passing signals are correct merged entries, conflict detection, no concurrent listing errors, and correct stat after recreate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_dir_test.go -->
