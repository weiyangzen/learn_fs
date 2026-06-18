## sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_all_objects.go

Purpose: Deletes every object from a bucket using pipelined listing and parallel deletion.

Important APIs/types/functions: `DeleteAllObjects(ctx, bucket)` uses `ListPrefix`, an object-name channel, and 64 deletion workers that call `bucket.DeleteObject`.

Control flow: one goroutine lists all objects into `minObjects`; a second goroutine extracts names into `objectNames`; workers drain names and delete. `errgroup.WithContext` cancels the pipeline on first error.

State and persistence behavior: destructively removes objects from the supplied bucket. Concurrent bucket updates produce undefined results and no rollback is attempted.

Dependencies and integration points: depends on `ListPrefix`, `gcs.Bucket`, `gcs.DeleteObjectRequest`, and `errgroup`; likely used in tests or cleanup utilities.

Risks: partial deletion on error, fixed high parallelism, and undefined behavior during concurrent writes. It ignores generations and deletes by name with default generation semantics.

Test signals: no direct test in this subset; integration cleanup behavior is the likely signal.
