# sources/object-store/minio/cmd/os-readdir_test.go

## Purpose
This test file validates MinIO's cross-platform `readDir` and `readDirN` behavior for error handling, regular files, directories, symlinks, and bounded listing.

## Important APIs, Types, and Functions
`TestReadDirFail` verifies nonexistent paths, file-as-directory behavior, and Linux permission-denied behavior. `setupTestReadDirEmpty`, `setupTestReadDirFiles`, `setupTestReadDirGeneric`, and `setupTestReadDirSymlink` build reusable fixtures. `TestReadDir` compares full listings after sorting. `TestReadDirN` checks count edge cases including zero, negative, exact, less-than, and greater-than counts.

## Control Flow and State
Tests create temporary directories and files, use `t.TempDir` plus explicit teardown, and sort entries before comparison because filesystem ordering is not stable. Symlink tests are skipped on Windows.

## Dependencies and Integration Points
The tests exercise `readDir`, `readDirN`, and platform-specific implementations indirectly. They depend on MinIO error values such as `errFileNotFound`, `globalWindowsOSName`, and slash-suffixed directory entries.

## Risks and Test Signals
The suite catches regressions in symlink filtering, directory suffix formatting, count handling, and error normalization. It does not assert ordering or low-level `ReadDirent` parsing, and permission tests are Linux-only because permission semantics vary by platform and user privileges.
