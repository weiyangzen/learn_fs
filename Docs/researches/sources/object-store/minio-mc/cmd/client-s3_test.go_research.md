# sources/object-store/minio-mc/cmd/client-s3_test.go

## Purpose

This test file provides lightweight HTTP-server coverage for the S3 client wrapper and select compression inference. It avoids a real S3 service by implementing minimal handlers for expected SDK calls.

## Important Tests And Control Flow

`bucketHandler` responds to list-buckets, list-objects, bucket location, PUT bucket, and HEAD requests. `objectHandler` validates authorization, accepts PUT bodies, returns object metadata for HEAD, supports basic multipart initiation/completion responses, lists incomplete uploads, and serves object bytes. `TestBucketOperations` builds `S3New` clients for bucket and root URLs, exercises `MakeBucket`, and checks list behavior for root, bucket without slash, and bucket with slash. `TestObjectOperations` uploads and downloads a small object. `TestSelectCompressionType` validates explicit compression override and extension/mime-based defaults for gzip, bzip2, parquet, csv, and json names.

## Dependencies, Risks, And Signals

Tests use `httptest`, `minio-go`, `gopkg.in/check.v1`, and shared test suite state. They confirm signing is present, URL path semantics influence list type, basic put/get work, and compression selection is stable. Gaps include delete, policy, versioning, notification, object lock, lifecycle, replication, encryption, CORS, virtual-host parsing, and error mapping.
