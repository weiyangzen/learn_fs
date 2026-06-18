## sources/sync-backup/kopia/internal/blobtesting/cleanup.go

Purpose: test helper for deleting old blobs from a storage backend.

Important APIs/types/functions: `MinCleanupAge` and `CleanupOldData`.

Control flow, state, and persistence: lists all blobs, compares timestamps against `clock.Now()`, enqueues deletes for old blobs in a `parallelwork.Queue`, and processes with concurrency 16. It intentionally ignores list errors but asserts delete queue processing succeeds.

Dependencies and integration points: used in storage integration tests to clean test data.

Risks and test signals: risk of deleting real data if pointed at a non-test storage/prefix, since it lists with empty prefix. No direct tests in this subset; callers must isolate test buckets/prefixes.
