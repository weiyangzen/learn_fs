# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/stat_test.go

Purpose: validates stat behavior with dentry cache enabled when backing GCS objects are updated or deleted outside the mount. It checks both cached stale attributes and refresh after TTL expiry.
Important APIs/types/functions: `statWithDentryCacheEnabledTest` suite, lifecycle methods, `TestStatWithDentryCacheEnabled`, and `TestStatWhenFileIsDeletedDirectlyFromGCS`.
Control flow: tests create an object, `os.Stat` the mounted file to cache the entry, mutate or delete the object directly on GCS, then stat immediately and after sleeping just over the configured two-second TTL.
State and persistence: backend object content/absence persists in GCS. Mounted stat results are expected to reflect cached state first, then refreshed GCS state after TTL expiry.
Dependencies and integration points: uses dentry setup fallback flags, Cloud Storage client helpers, `operations.GenerateRandomData`, `client.WriteToObject`, `client.DeleteObjectOnGCS`, and `time.Sleep`.
Risks and edge cases: fixed `2100ms` sleep is close to TTL and can be flaky on slow environments or if cache expiration uses coarse scheduling. It does not inspect logs, relying on observed sizes and errors.
Test signals: immediate stat returns initial size despite backend mutation/deletion; post-TTL stat returns updated size or not-found. Failures isolate stale/expiry behavior in metadata/dentry cache.
