<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/etcd.go -->
# sources/object-store/minio/cmd/etcd.go

## Purpose
Wraps etcd v3 key operations used by MinIO configuration and bucket DNS/federation code, normalizing timeout errors and applying a consistent operation timeout.

## Important APIs, types, and functions
- `errEtcdUnreachable` is the user-facing sentinel for deadline failures.
- `etcdErrToErr` maps nil, `context.DeadlineExceeded`, and other etcd errors into MinIO-style errors with endpoint context.
- `saveKeyEtcdWithTTL`, `saveKeyEtcd`, `deleteKeyEtcd`, and `readKeyEtcd` implement grant/put, put, delete, and get operations.

## Control flow
Every public helper creates a timeout context with `defaultContextTimeout`. TTL saves first grant a lease, then put the key with that lease. Normal saves optionally delegate to TTL mode. Reads return `errConfigNotFound` if etcd returns no matching key.

## State and persistence behavior
State is persisted in the configured etcd cluster under caller-provided keys. TTL writes depend on etcd lease expiration. The helper itself stores no process-local state.

## Dependencies and integration points
The file depends on `go.etcd.io/etcd/client/v3`, MinIO logging helpers, `defaultContextTimeout`, `options` with TTL, and `errConfigNotFound`. It is used by centralized config, bucket DNS, federation, and health/readiness code that checks `globalEtcdClient`.

## Risks and edge cases
Only `context.DeadlineExceeded` is treated as unreachable; other connectivity failures become generic unexpected errors. TTL grant uses the same timeout as put, so slow etcd can fail before writes occur. `readKeyEtcd` iterates returned KVs even though exact-key reads normally return only one match.

## Test signals
No direct tests in this group. Expected signals are integration paths that simulate missing config, unreachable etcd in readiness checks, and successful centralized config reads/writes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/etcd.go -->
