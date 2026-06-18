## sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_prefix.go

Purpose: Streams all objects with a given prefix into a caller-provided channel.

Important APIs/types/functions: `ListPrefix(ctx, bucket, prefix, minObjects)` builds `gcs.ListObjectsRequest{Prefix: prefix}` and sends each `MinObject` through `minObjects`.

Control flow: paginates via continuation token, sends each page's objects, and respects context cancellation while sending. It wraps list errors as `ListObjects: ...`.

State and persistence behavior: no persistence; caller owns channel closure.

Dependencies and integration points: used by `DeleteAllObjects` and fixture/listing utilities.

Risks: if receiver does not drain the channel, the function blocks until context cancellation. It does not emit collapsed runs, only objects.

Test signals: no direct test in this subset.
