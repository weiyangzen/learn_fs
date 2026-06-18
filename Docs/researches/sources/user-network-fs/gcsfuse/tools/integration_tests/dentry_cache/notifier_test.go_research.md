# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/notifier_test.go

Purpose: tests dentry-cache notifier behavior after stale read/write/delete errors. It ensures the first operation detects an externally changed or deleted object, invalidates cached kernel metadata, and allows the next operation to observe fresh state before TTL expiry.
Important APIs/types/functions: `notifierTest` suite lifecycle mirrors other dentry tests. Core tests are `TestWriteFileWithDentryCacheEnabled`, `TestReadFileWithDentryCacheEnabled`, and `TestDeleteFileWithDentryCacheEnabled`.
Control flow: each test creates or deletes GCS state behind the mounted path after an initial `os.Stat` warms cache. The first read/write is expected to raise ESTALE; the second read/write should succeed after notifier invalidation. Delete case expects a later `os.Stat` to report missing.
State and persistence: GCS is the source of truth while kernel and metadata caches are intentionally stale. Notifier side effects are transient cache invalidations, not persistent object changes except for test writes.
Dependencies and integration points: uses `client.SetupFileInTestDirectory`, `WriteToObject`, `DeleteObjectOnGCS`, `operations.WriteFile`, `ReadFile`, and `ValidateESTALEError`. It relies on high TTL fallback config so success is attributable to notifier behavior rather than expiry.
Risks and edge cases: ordering assumes immediate notifier invalidation after the first failed operation. Log-based confirmation is absent; behavior is inferred from the second operation and stat result.
Test signals: ESTALE on the first clobbered access plus success/fresh not-found on the next access validates notifier-driven dentry invalidation.
