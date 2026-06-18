# sources/object-store/minio-mc/cmd/client-s3.go

## Purpose

`client-s3.go` is the S3/object-storage implementation of mc's shared `Client` interface. It wraps `minio-go` to support bucket/object I/O, listing, incomplete uploads, versioned listing, notifications, select, presigned sharing, access policy, object lock, tags, lifecycle, versioning, replication, encryption, bucket info, restore, object parts, and CORS.

## Important APIs, Types, And Control Flow

`S3Client` stores a target `ClientURL`, cached `minio.Client`, virtual-host style flag, and a mutex around list/stat operations. `newFactory` creates `S3New`, a closure that hashes endpoint and credentials to cache `minio.Client` instances, builds transports from `Config`, installs chain credentials, handles virtual-host/accelerated endpoints, and sets app info. Custom dialers enforce connection deadlines and optional resolver overrides.

I/O methods translate mc options into SDK options. `Get` uses `minio.Core.GetObject`, handles ranges, versions, zip extraction, SSE, and typed error mapping. `Put` separates headers from user metadata, parses tags and object-lock headers, configures multipart/checksum/SSE/storage-class options, and maps SDK errors to mc errors. `Copy` selects single-copy or compose based on size/multipart settings. `Remove` streams batched deletes per bucket, handles incomplete uploads, forced delete, bucket removal, governance bypass, and async SDK error draining.

Listing paths include bucket listing, regular object listing, zip extraction listing, incomplete upload listing, versioned listing with fallback when unsupported, prefix-as-directory detection, and conversion from `minio.ObjectInfo` to `ClientContent`. Control helpers split bucket/object paths, detect AWS/GCS virtual-host support, and build URL paths.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is remote S3-compatible service state: objects, buckets, bucket configs, policies, object-lock metadata, tags, lifecycle, versioning, replication, encryption, notifications, and incomplete uploads. Dependencies are broad: `minio-go`, notification/policy/tags/SSE/replication/lifecycle packages, mc transports, env config, deadline connections, custom global roots/resolvers, and shared errors. Risks include cached client reuse across mutable configs, virtual-host bucket parsing, provider-specific listing differences, versioning fallback, delete-channel deadlocks, object-lock header parsing, metadata filtering, and feature availability differences. Tests cover bucket/object operations through httptest, select compression inference, and STS credential-chain operation; many advanced bucket configuration APIs depend on integration testing.
