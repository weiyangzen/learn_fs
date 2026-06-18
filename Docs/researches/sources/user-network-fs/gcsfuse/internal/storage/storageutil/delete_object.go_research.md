## sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_object.go

Purpose: Thin helper to delete one object by name.

Important APIs/types/functions: `DeleteObject(ctx, bucket, name)` creates `gcs.DeleteObjectRequest{Name: name, Generation: 0}` and delegates to `bucket.DeleteObject`.

Control flow: no retry or precondition logic in the helper.

State and persistence behavior: removes a named object from the bucket according to bucket implementation semantics.

Dependencies and integration points: used by test utilities and callers needing a concise delete wrapper.

Risks: generation is hard-coded to zero, so callers needing generation-specific deletes cannot use this helper.

Test signals: no direct test in this subset.
