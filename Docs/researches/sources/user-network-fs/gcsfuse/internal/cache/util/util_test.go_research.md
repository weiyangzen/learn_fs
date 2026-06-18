<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/util/util_test.go

Purpose: tests cache utility helpers for local file creation, path normalization, invalid-handle error classification, CRC calculation, truncating removal, cache-directory validation, memory alignment, and aligned copying for direct I/O.

Important APIs/types/functions: ogletest suite `utilTest`, helper `assertFileAndDirCreationWithGivenDirPerm`, tests for `CreateFile`, `GetDownloadPath`, `IsCacheHandleInvalid`, `CalculateFileCRC32`, `TruncateAndRemoveFile`, `CreateCacheDirectoryIfNotPresentAt`, `GetMemoryAlignedBuffer`, and `CopyUsingMemoryAlignedBuffer`.

Control flow: suite setup builds a `data.FileSpec` under the current user's home directory and removes prior test directories. `CreateFile` tests vary directory presence, permissions, open flags, file permissions, existing files, and relative paths. Standalone `testing` table tests create temp directories or random local files, optionally open with `syscall.O_DIRECT`, then assert write sizes and file contents after aligned copying.

State and persistence: creates and removes files/directories under the user's home directory, relative working directory, and random local test files. Tests inspect Unix owner/group and permission bits using `syscall.Stat_t`, so they are OS-sensitive.

Dependencies and integration points: depends on `operations.RemoveDir`, `internal/util.GenerateRandomBytes`, `testify`, ogletest, `syscall.O_DIRECT`, and `testdata/validfile.txt` plus `testdata/emptyfile.txt`. It validates filesystem behavior relied on by file cache setup and sparse/direct cache writing.

Risks: tests assume Unix permission semantics and may behave differently on non-Linux platforms or with unusual umask/filesystem behavior. O_DIRECT cases require alignment-sensitive local filesystem support. One test name says `Test_getObjectPath` but calls `GetDownloadPath`, so it may not directly cover `GetObjectPath`.

Test signals: broad coverage catches permission regressions, wrapped sentinel matching, context cancellation propagation, padding semantics for non-aligned content sizes, invalid buffer sizes, and invalid O_DIRECT write offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util_test.go -->
