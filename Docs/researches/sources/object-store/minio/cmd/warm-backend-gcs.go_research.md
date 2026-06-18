# sources/object-store/minio/cmd/warm-backend-gcs.go

GCS implementation of `WarmBackend`. It prefixes object keys, writes metadata/storage class through a GCS object writer, reads ranges with `ReadCompressed(true)` to avoid decompressive transcoding, deletes objects, lists one object for `InUse`, and maps GCS/googleapi errors to MinIO object errors.

State is remote GCS data and metadata. Construction validates credential JSON and bucket, creates a read/write scoped client, and sets a tier User-Agent.

Key risk: `PutWithMeta` calls `xioutil.Copy(w, data)` twice before `Close`; usually the second copy sees EOF, but unusual readers can block, duplicate, or raise errors. GCS remote version IDs are currently unsupported. No direct tests in this subset cover it.
