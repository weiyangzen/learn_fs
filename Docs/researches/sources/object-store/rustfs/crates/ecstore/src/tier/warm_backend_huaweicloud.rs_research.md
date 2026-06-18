# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_huaweicloud.rs

## Purpose

Huawei Cloud OBS warm-tier adapter over the S3-compatible transition client.

## Important APIs and Types

`WarmBackendHuaweicloud(WarmBackendS3)`, constructor, `WarmBackend` impl, and multipart `optimal_part_size`.

## Control Flow

Validates credentials/bucket, parses endpoint, creates Signature V4 credentials, enables trailing headers and DNS bucket lookup, creates provider id `"huaweicloud"`, wraps S3 backend, and delegates reads/removes/in-use. Upload sets part size and disables content SHA256.

## State and Persistence Behavior

Only in-memory client/config locally; remote object state lives in configured bucket/prefix.

## Dependencies and Integration Points

Uses `TierHuaweicloud`, transition API credentials/client, `WarmBackendS3`, and shared metadata conversion.

## Risks and Edge Cases

Huawei-specific error/auth behavior is not explicit. `tier` is unused and tests are absent.

## Test Signals

No direct tests; should mirror compatible-provider credential, endpoint, part-size, prefix, and CRUD coverage.
