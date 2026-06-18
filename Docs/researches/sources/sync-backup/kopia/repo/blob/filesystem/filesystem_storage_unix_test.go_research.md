# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_unix_test.go

Purpose: Unix-specific test for stale file handle error handling in filesystem storage.

Important APIs/types/functions: `TestFileStorage_ESTALE_ErrorHandling`, Unix `ESTALE` behavior through mock OS/stat/open/remove/list paths, and filesystem retry classification.

Control flow: the test injects stale errors and verifies they are treated as non-retriable or handled according to filesystem provider expectations. It complements cross-platform mock tests with Unix errno-specific behavior.

State and persistence behavior: mock/local filesystem state only. No durable external state is used.

Dependencies/integration points: validates `realOS.IsStale`/`fsImpl.isRetriable` semantics on Unix. Risks include platform build constraints, errno differences across Unix variants, and limited coverage on non-Unix CI. The test protects against retry loops on stale handles, which can otherwise mask real filesystem invalidation.
