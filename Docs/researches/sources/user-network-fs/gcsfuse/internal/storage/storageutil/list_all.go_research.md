## sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_all.go

Purpose: Collects all pages for a `ListObjectsRequest`.

Important APIs/types/functions: `ListAll(ctx, bucket, req)` returns accumulated `[]*gcs.MinObject`, collapsed runs, and error; it mutates `req.ContinuationToken`.

Control flow: repeatedly calls `bucket.ListObjects`, appends objects and collapsed runs, exits when continuation token is empty, otherwise updates the request token.

State and persistence behavior: no persistent state, but it mutates the caller-provided request.

Dependencies and integration points: used by tests or higher-level listing helpers over `gcs.Bucket`.

Risks: callers reusing `req` after failure or completion see its continuation token changed. It accumulates all results in memory and may be expensive for large buckets.

Test signals: no direct local test; behavior can be validated via fake bucket paging tests.
