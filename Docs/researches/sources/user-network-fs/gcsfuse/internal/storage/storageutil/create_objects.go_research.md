## sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_objects.go

Purpose: Parallel helper for creating multiple objects from a name-to-contents map.

Important APIs/types/functions: `CreateObjects(ctx, bucket, input)` uses `errgroup.WithContext`, a buffered channel of records, and a fixed parallelism of 64 workers.

Control flow: all records are enqueued before workers start; each worker drains the channel and calls `CreateObject`. First error cancels the errgroup context and is returned by `group.Wait`.

State and persistence behavior: persists a subset or all requested objects depending on when errors occur. No rollback is attempted.

Dependencies and integration points: depends on `CreateObject`, `gcs.Bucket`, and `golang.org/x/sync/errgroup`; useful for test fixture setup.

Risks: fixed parallelism can be excessive for small inputs or constrained fake services. Map iteration makes creation order nondeterministic. Partial creation on error is possible.

Test signals: no direct local test; correctness depends on bucket fake/integration tests.
