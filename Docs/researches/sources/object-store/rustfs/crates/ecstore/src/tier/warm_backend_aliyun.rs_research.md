# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_aliyun.rs

## Purpose

Aliyun OSS warm-tier adapter over the RustFS transition-client S3-compatible wrapper.

## Important APIs and Types

`WarmBackendAliyun(WarmBackendS3)`, `new`, `WarmBackend` impl, and `optimal_part_size` with 5 TiB max, 10,000 parts, and 128 MiB minimum part size.

## Control Flow

Constructor validates keys/bucket, parses endpoint, creates Signature V4 credentials, enables trailing headers and DNS bucket lookup, builds an Aliyun transition client, and wraps bucket/prefix. Upload computes part size, promotes metadata, disables content SHA256, and delegates to `put_object`; get/remove/in-use delegate to wrapped S3.

## State and Persistence Behavior

Only in-memory client/config locally; remote objects are persisted/removed in configured bucket/prefix.

## Dependencies and Integration Points

Depends on `TierAliyun`, transition API client/credentials, shared warm-backend metadata handling, and `WarmBackendS3`.

## Risks and Edge Cases

Provider-specific signing is delegated to `TransitionClient`. `tier` argument is unused. `-1` object size maps to max object size for part calculation. Disabling content SHA256 is a compatibility/integrity tradeoff.

## Test Signals

No direct tests; should cover credentials, endpoint host, prefix, part-size bounds, and CRUD.
