# sources/object-store/minio/cmd/os-reliable_test.go

## Purpose
This test file verifies MinIO's reliable filesystem wrappers for mkdir-all and rename-all behavior.

## Important APIs, Types, and Functions
`TestOSMkdirAll` creates an XL storage setup, asserts empty path returns `errInvalidArgument`, asserts an overlong object path returns `errFileNameTooLong`, and checks successful nested directory creation. `TestOSRenameAll` creates a source volume, checks invalid source/destination handling, verifies a successful rename, confirms a second rename reports `errFileNotFound`, and tests long source and destination path failures.

## Control Flow and State
Tests rely on `newXLStorageTestSetup` to create storage-like paths. They call `mkdirAll` and `renameAll` directly and compare exact MinIO error values.

## Dependencies and Integration Points
The test uses path joining and XL setup helpers from the surrounding cmd test framework. It validates the behavior exposed to storage code rather than platform-specific syscall behavior.

## Risks and Test Signals
The tests cover validation and core success/error mapping, but do not simulate racing parent deletion, ENOTEMPTY removal races, cross-device renames, or Windows-specific path-not-found/not-directory ambiguity.
