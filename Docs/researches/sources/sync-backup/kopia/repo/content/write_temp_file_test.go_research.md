# sources/sync-backup/kopia/repo/content/write_temp_file_test.go

## Purpose
Tests the temporary-file helper's success path, directory creation, durability call, and cleanup behavior under failures.

## Important APIs, Types, And Functions
Tests include `TestWriteTempFileAtomic_HappyPath`, `TestWriteTempFileAtomic_EmptyData`, `TestWriteTempFileAtomic_CreatesDirectoryIfMissing`, `TestWriteTempFileAtomic_NonExistentDirUnwritable`, `TestWriteTempFileAtomic_FileIsSynced`, `TestWriteTempFileAtomic_NoTempFilesLeft`, and `TestWriteTempFileAtomic_NoTempFilesLeftOnError`. Test doubles include `mockFileSynced`, `mockfs`, `mockFileWriteError`, `mockFileSyncError`, and `mockFileCloseError`.

## Control Flow
The tests call `writeTempFileAtomicImp` with `localFS` or wrapped file implementations, inspect returned paths, read file contents, and list target directories. Failure tests inject write, sync, and close errors and assert that the returned name is empty and no temp files remain.

## State And Persistence
Each test uses `t.TempDir`. Successful tests leave exactly the returned temp file in the directory; failure tests expect the directory to be empty. The permission test temporarily chmods a parent directory and restores it in cleanup.

## Dependencies And Integration Points
Uses `os`, `filepath`, `runtime`, `atomic`, `pkg/errors`, and `testify/require`. The mocked filesystem path exercises the file abstraction built into production code.

## Risks And Edge Cases
The unwritable-directory test is skipped on Windows and when running as root because permissions may not behave as expected. Tests do not cover short writes with nil error or remove failures during cleanup.

## Test Signals
Coverage is focused and high for intended helper behavior, especially the subtle deferred close/cleanup path.
