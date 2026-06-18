## sources/user-network-fs/gcsfuse/internal/storage/storageutil/read_object.go

Purpose: Reads an entire object's latest generation into memory.

Important APIs/types/functions: `ReadObject(ctx, bucket, name)` creates `gcs.ReadObjectRequest`, calls `bucket.NewReaderWithReadHandle`, defers close, and returns `io.ReadAll` bytes.

Control flow: reader construction errors return directly; read errors are wrapped as `ReadAll`; close errors are returned only if no previous error occurred.

State and persistence behavior: no persistence; consumes a storage reader and closes it.

Dependencies and integration points: depends on `gcs.Bucket`, `gcs.StorageReader`, and Go `io`.

Risks: reads whole object into memory, unsuitable for large objects. It does not request a specific generation or byte range.

Test signals: no direct test in this subset; behavior is simple and suited for fixture assertions.
