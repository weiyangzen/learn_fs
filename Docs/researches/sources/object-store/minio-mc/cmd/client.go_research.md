# sources/object-store/minio-mc/cmd/client.go

## Purpose

`client.go` defines the shared client contract and common option/content/config types that let mc commands operate uniformly against S3-compatible services and local filesystems.

## Important APIs, Types, And Control Flow

`DirOpt` controls whether directory entries appear before objects, after objects, or not at all. `GetOptions`, `PutOptions`, `StatOptions`, `BucketStatOptions`, `ListOptions`, and `CopyOptions` carry operation-specific flags such as SSE, version IDs, zip extraction, multipart settings, checksums, retention metadata, preserve mode, and listing modes. `Client` is the large interface implemented by `fsClient` and `S3Client`, covering common stat/list, bucket operations, object I/O, object locking, sharing, watch, remove, tags, lifecycle, versioning, replication, encryption, bucket info, restore, object-part, and CORS operations.

`ClientContent` is the normalized metadata carrier for list/stat/get flows, with URL, bucket, size, mode, storage class, HTTP metadata, user metadata, tags, checksum, ETag, retention/legal hold, versioning, replication, restore, and embedded error. `Config` contains S3 alias credentials, endpoint, debug, TLS, lookup, deadlines, limits, and transport. `getCredsChain` builds static and optional STS web-identity credentials. `initTransport` creates deadline-aware transports, TLS config, custom headers, bandwidth limiter, debug tracers or certificate-expiry notifier, and gzip support.

## State, Dependencies, Integration, Risks, And Tests

State includes cached `Config.Transport`, process environment mutation for STS variables, and global certificate-expiry records. Dependencies include minio-go, credentials, encryption/lifecycle/replication/CORS packages, `gzhttp`, limiter, httptracer, env helpers, and global TLS/header settings. Risks are a very broad interface forcing many filesystem stubs, process-wide STS environment changes, transport reuse with mutable configs, and debug tracer leakage. Tests in S3/STS files cover credential-chain and transport paths indirectly.
