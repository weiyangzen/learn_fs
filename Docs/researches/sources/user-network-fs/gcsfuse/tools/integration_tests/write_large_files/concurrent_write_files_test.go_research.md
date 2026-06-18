# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_files_test.go

Purpose: integration test for concurrently writing multiple large files through gcsfuse.

Important APIs/types/functions: `TestWriteMultipleFilesConcurrently`, `DirForConcurrentWrite`, `errgroup.Group`, `operations.WriteFilesSequentially`, and `operations.AreFilesIdentical`.

Control flow: creates a test directory, generates three file names, starts one errgroup task per file, writes identical 500 MiB content to a local temp file and mounted file, then compares them.

State/persistence behavior: writes large local temp files under `/tmp` and large objects through the mounted gcsfuse directory; temp local files are removed via `t.Cleanup`.

Dependencies/integration: relies on `write_large_files_test.go` setup, static mounting, direct I/O helpers, and the bucket backend.

Risks/test signals: the errgroup wait result is ignored, so goroutine-returned errors would not fail the test except where helper assertions fail inside goroutines. It stresses global write-block limits and parallel object creation.
