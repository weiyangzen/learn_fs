# sources/sync-backup/kopia/repo/blob/s3/s3_storage.go

Purpose: implements Kopia's `blob.Storage` provider for S3-compatible object stores using `minio-go`, including object reads, writes, metadata, listing, deletion, retention extension, TLS customization, credentials, and repository-local storage-class configuration.

Important APIs/types/functions: `s3Storage` embeds `Options` and `blob.DefaultProviderImplementation` and owns a `*minio.Client` plus optional `StorageConfig`. Public storage methods are `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `ConnectionInfo`, `String`, and `DisplayName`. Constructors are `New`, `newStorage`, and `newStorageWithCredentials`; `getCustomTransport` controls TLS verification and Root CA support; `translateError` maps provider errors to blob-layer sentinels.

Control flow: `New` builds the raw storage, optionally wraps it for point-in-time behavior, then returns a retrying wrapper. Reads set S3 byte ranges for partial and zero-length reads, stream from `GetObject`, and validate exact length. Writes reject unsupported `DoNotRecreate` and `SetModTime`, derive per-prefix storage class, optionally set S3 Object Lock retention, upload with multipart disabled and MD5 enabled, and then read back modtime when requested. Startup builds static/env/IAM or STS-assume-role credentials, creates a MinIO client, and loads `.storageconfig` if present.

State and persistence behavior: user data is stored as S3 objects named `Prefix + blobID`; `.storageconfig` is hidden from normal listing. S3 server timestamps and version IDs become metadata where available. Retention uses provider object-lock state, and deletes are idempotent when the object is absent.

Dependencies/integration: integrates with `blob.AddSupportedStorage("s3", Options{}, New)`, `retrying`, `maybePointInTimeStore`, MinIO S3 APIs, Kopia gather buffers, clock abstraction for retention, and blob sentinel errors consumed by higher repository layers.

Risks and edge cases: S3 error messages are partly string-matched for expired tokens. Zero-length range handling uses a fake range and skips reading. `PutObject` has a special EOF/empty-stream path. Object lock requires valid retention mode and provider support; MD5 behavior matters for locked AWS buckets. TLS options can intentionally disable verification, so callers must treat that as a security-sensitive configuration.

Test signals: `s3_storage_test.go` covers AWS, MinIO, STS, custom assume-role credentials, invalid credentials fast failure, token expiration, object lock/retention behavior, TLS bypass and provided root CAs, provider validation, connection-info round trips, and cleanup behavior.
