# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/file_operations.go

Purpose: broad file-operation helper library for integration tests, including direct I/O reads/writes, content comparison, stat validation, checksum helpers, temp-file creation, GCS object utilities, and sync/error assertions.

Important APIs/types/functions: `CopyFile`, `WriteFileInAppendMode`, `WriteFile`, `ReadFileSequentially`, `WriteChunkOfRandomBytesToFiles`, `WriteFilesSequentially`, `ReadChunkFromFile`, `AreFilesIdentical`, `GetGcsObjectSize`, `CreateFile`, `OpenFiles`, `VerifyStatFile`, `CreateFileOfSize`, `CalculateFileCRC32`, `CreateLocalTempFile`, `ReadAndCompare`, `CreateLocalFile`, `ValidateSyncGivenThatFileIsClobbered`, and `StatFileOrFatal`.

Control flow: most helpers fail tests directly through `testing.TB` or return wrapped errors. Large-write helpers open matching local and mounted files, write identical random chunks at offsets, optionally sync, and compare byte-for-byte using fixed-size buffers.

State/persistence behavior: heavily mutates local files, mounted gcsfuse files, temp files under `/tmp`, and GCS objects through `gcloud`. It also waits after close/sync for zonal buckets to observe size updates.

Dependencies/integration: used across write, read, local-file, gzip, streaming-writes, and stale-handle tests. Depends on `setup`, internal GCS storage abstractions, `testify`, gzip, CRC32, and Linux `O_DIRECT`.

Risks/test signals: direct I/O imposes alignment constraints, and some helpers call fatal logging or exit indirectly via `CloseFile`. `CreateFileOfSize` converts random bytes to string, which can be memory-heavy for large files.
