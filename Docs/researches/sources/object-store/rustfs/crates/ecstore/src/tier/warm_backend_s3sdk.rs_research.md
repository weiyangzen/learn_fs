# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3sdk.rs

## Purpose

Alternate generic S3 adapter using the official AWS SDK for Rust.

## Important APIs and Types

Defines module-local `WarmBackendS3` with `Arc<aws_sdk_s3::Client>`, bucket, prefix, and storage class. Uses AWS SDK `Credentials`, `RegionProviderChain`, `Client`, and `ByteStream`.

## Control Flow

Constructor validates endpoint/credentials/bucket, builds static AWS credentials, configures endpoint URL and region, and creates a client. Put buffers the reader into `ByteStream` and sends `put_object`. Get applies optional version/range, collects the full response body, and returns a cursor. Remove sends delete. `in_use` lists bucket contents.

## State and Persistence Behavior

No local persistence; remote S3 stores data. Put/get currently buffer full objects in memory.

## Dependencies and Integration Points

Declared in `mod.rs`, but the visible factory imports transition-client `warm_backend_s3::WarmBackendS3`, so this appears unused unless explicitly selected elsewhere.

## Risks and Edge Cases

Ignores metadata and storage class in `put_with_meta`, lists bucket root rather than prefix with max-keys, buffers full objects, and validates but does not implement AWS role/web identity.

## Test Signals

No tests; enabling it needs coverage for metadata, prefix-scoped in-use, streaming memory behavior, ranges, endpoint compatibility, and credentials.
