# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_file_test.go

Purpose: Verifies single-file copy semantics through GCSFuse: the copied file is created at a new path, content matches the source, and the source remains unchanged.

Important APIs/types/functions: `TestCopyFile` uses `setup.SetupTestDirectory`, `operations.CreateFileWithContent`, `operations.ReadFile`, `os.Stat`, `operations.CopyFile`, and `setup.CompareFileContents`.

Control flow: the test creates a randomized temp file under `dirForOperationsTest`, reads its original content, asserts the destination does not already exist, copies the file, then validates both destination and source contents. Defers remove source and destination files.

State/persistence: State lives in the mounted operations test directory and maps to GCS objects. The test depends on close/flush behavior inside `CreateFileWithContent` and `CopyFile` so the subsequent reads see durable content.

Dependencies/integration: Shares `tempFileName` and `Content` constants with `write_test.go`/`operations_test.go`; uses common operations/setup helpers.

Risks/test signals: The destination name is derived by appending `Copy`, so stale objects from failed cleanup could cause a precondition failure. Passing indicates basic object copy and read-after-copy consistency.
