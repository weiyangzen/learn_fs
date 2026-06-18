## sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_empty_objects.go

Purpose: Convenience helper to create many empty GCS objects.

Important APIs/types/functions: `CreateEmptyObjects(ctx, bucket, names)` builds a `map[string][]byte` with nil contents for each name and delegates to `CreateObjects`.

Control flow: linear conversion from names slice to map, then parallel creation via `CreateObjects`.

State and persistence behavior: persists objects to the supplied `gcs.Bucket`; duplicate names collapse due to map keys.

Dependencies and integration points: depends on `CreateObjects` and internal `gcs.Bucket`. Useful for tests and fixture setup.

Risks: duplicate input names are silently de-duplicated and creation order is undefined. Errors are only those returned by `CreateObjects`.

Test signals: no direct test in this subset; behavior is simple delegation.
