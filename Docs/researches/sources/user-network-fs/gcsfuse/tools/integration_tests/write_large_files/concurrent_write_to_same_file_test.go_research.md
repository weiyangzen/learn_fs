# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_to_same_file_test.go

Purpose: integration test for concurrent writes to disjoint offsets in the same mounted file.

Important APIs/types/functions: `TestWriteToSameFileConcurrently` and helper `writeToFileSequentially`.

Control flow: creates local and mounted files, starts five goroutines, assigns each a non-overlapping 10 MiB range within a 50 MiB region, writes matching random 1 MiB chunks to both files, waits for all writers, and compares mounted content with local content.

State/persistence behavior: mutates one local temp file and one mounted gcsfuse file concurrently. On zonal buckets, files are explicitly synced after each writer completes.

Dependencies/integration: depends on `operations.OpenFiles`, `WriteChunkOfRandomBytesToFiles`, `SyncFiles`, and the package-level setup/mount state.

Risks/test signals: concurrent writes to the same local file and mounted file assume disjoint offsets avoid racey content conflicts. The main test checks errgroup errors and byte equality.
