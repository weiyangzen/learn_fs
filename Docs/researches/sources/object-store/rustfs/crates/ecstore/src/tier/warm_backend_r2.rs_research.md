# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_r2.rs

## Purpose

Cloudflare R2 warm-tier adapter over the S3-compatible transition-client layer.

## Important APIs and Types

`WarmBackendR2(WarmBackendS3)`, constructor, `WarmBackend` impl, and multipart part-size helper.

## Control Flow

Validates credentials/bucket, parses endpoint, creates Signature V4 credentials with trailing headers, builds provider id `"r2"`, wraps S3 backend, uploads with part size and disabled SHA256, and delegates read/remove/in-use.

## State and Persistence Behavior

No local persistence; remote R2 bucket/prefix stores data.

## Dependencies and Integration Points

Uses `TierR2`, transition client types, `WarmBackendS3`, and shared metadata conversion.

## Risks and Edge Cases

R2 account endpoint and region conventions are not validated beyond URL host parsing. Content SHA256 is disabled. No provider-specific tests.

## Test Signals

No direct tests; should cover endpoint validation, credentials, part sizing, prefix behavior, in-use, and error mapping.
