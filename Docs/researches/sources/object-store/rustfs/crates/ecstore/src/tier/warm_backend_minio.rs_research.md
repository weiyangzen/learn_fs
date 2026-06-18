# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_minio.rs

## Purpose

MinIO-compatible warm-tier adapter over the transition-client S3 wrapper.

## Important APIs and Types

`WarmBackendMinIO(WarmBackendS3)`, constructor, `WarmBackend` impl, and multipart sizing helper.

## Control Flow

Validates credentials/bucket, parses endpoint, creates Signature V4 credentials with trailing headers, builds provider id `"minio"`, wraps S3 backend, uploads with computed part size and disabled content SHA256, and delegates get/remove/in-use.

## State and Persistence Behavior

No durable local state; remote MinIO bucket/prefix holds tiered objects.

## Dependencies and Integration Points

Uses `TierMinIO`, transition client APIs, `WarmBackendS3`, and shared put option conversion.

## Risks and Edge Cases

No explicit bucket lookup override; path-style versus virtual-host behavior depends on transition client. Provider errors surface as generic IO errors. Tests are absent.

## Test Signals

No direct tests; should cover endpoint style, credentials, prefix joining, multipart, object-lock metadata, and `in_use`.
