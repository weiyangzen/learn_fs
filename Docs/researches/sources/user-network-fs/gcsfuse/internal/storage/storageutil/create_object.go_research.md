## sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_object.go

Purpose: Thin wrapper for creating one object with byte-slice contents.

Important APIs/types/functions: `CreateObject(ctx, bucket, name, contents)` creates `gcs.CreateObjectRequest{Name, Contents: bytes.NewReader(contents)}` and calls `bucket.CreateObject`.

Control flow: no retries or attribute handling; all behavior is delegated to the bucket implementation.

State and persistence behavior: writes one object to the remote or fake bucket.

Dependencies and integration points: used by `CreateObjects` and tests needing direct object setup.

Risks: no checksum, metadata, generation precondition, or content-type support. Callers needing those must use `gcs.CreateObjectRequest` directly.

Test signals: indirectly covered by helpers that create/list/read/delete fake bucket objects.
