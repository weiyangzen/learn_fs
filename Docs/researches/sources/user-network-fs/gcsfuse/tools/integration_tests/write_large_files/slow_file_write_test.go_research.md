# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/slow_file_write_test.go

Purpose: integration test for slow large writes with long pauses between synced chunks.

Important APIs/types/functions: `TestSlowWriteToFile` and `DirForSlowWrite`.

Control flow: opens a mounted file with `O_DIRECT`, generates a 33 MiB string, writes it twice, syncs after each write, asserts byte counts, and sleeps 40 seconds between writes to exceed the referenced 32 second chunk retry deadline.

State/persistence behavior: creates and syncs a mounted gcsfuse file. No local oracle file is used.

Dependencies/integration: uses `operations.OpenFileWithODirect`, `operations.SyncFile`, and setup random-string generation.

Risks/test signals: expensive and timing-sensitive by design. It checks write/sync success but not final file content or size explicitly.
