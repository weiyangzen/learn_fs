# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_tencent.rs

## Purpose

Tencent COS warm-tier adapter over the transition-client S3-compatible wrapper.

## Important APIs and Types

`WarmBackendTencent(WarmBackendS3)`, constructor, `WarmBackend` impl, and multipart sizing helper.

## Control Flow

Validates credentials/bucket, parses endpoint, creates Signature V4 credentials, enables trailing headers and DNS bucket lookup, builds provider id `"tencent"`, wraps S3 backend, uploads with computed part size and disabled content SHA256, and delegates get/remove/in-use.

## State and Persistence Behavior

No local durable state; remote Tencent bucket/prefix stores tiered objects.

## Dependencies and Integration Points

Uses `TierTencent`, transition API credentials/client, `WarmBackendS3`, and shared metadata conversion.

## Risks and Edge Cases

Tencent-specific signing, endpoint, and region rules are delegated to transition client. `tier` is unused. No direct tests cover provider behavior.

## Test Signals

No direct tests; should cover credentials, endpoint parsing, bucket lookup, multipart options, prefix, and CRUD.
