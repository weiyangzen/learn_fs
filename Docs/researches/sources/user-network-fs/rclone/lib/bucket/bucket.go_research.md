
# sources/user-network-fs/rclone/lib/bucket/bucket.go

Purpose: utility package for bucket-based backend path handling and bucket existence/deletion caching.

Important APIs/types/functions: `ErrAlreadyDeleted`, `Split`, `Join`, `IsAllSlashes`, `Cache`, `NewCache`, `MarkOK`, `MarkDeleted`, `Create`, `Remove`, and `IsDeleted`. `CreateFn` and `ExistsFn` abstract backend operations.

Control flow: `Split` separates first path component as bucket. `Join` concatenates without cleaning to preserve slashes. `Cache.Create` serializes creates, optionally re-checks externally deleted buckets, calls `create`, and marks success. `Cache.Remove` serializes removes and returns `ErrAlreadyDeleted` for known-deleted buckets. Separate create/remove mutexes avoid simultaneous conflicting operations.

State/persistence: `Cache.status` is an in-memory map of bucket name to known present/deleted.

Dependencies/integration: used by bucket-based backends to avoid redundant creates/removes and to preserve path semantics that `path.Join` would normalize away.

Risks: cache can become stale if buckets are changed externally. `Create`/`Remove` unlock the map around user callbacks, so status may change concurrently; outer create/remove mutexes limit same-operation races but not all external effects.

Test signals: `bucket_test.go` covers path functions and cache state transitions/errors.
