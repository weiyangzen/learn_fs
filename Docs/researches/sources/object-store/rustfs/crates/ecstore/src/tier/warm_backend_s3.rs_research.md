# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_s3.rs

## Purpose

Primary generic S3 warm-tier adapter using RustFS's transition-client abstraction.

## Important APIs and Types

`WarmBackendS3` holds `TransitionClient`, `TransitionCore`, bucket, prefix, and storage class. `new`, `get_dest`, and the `WarmBackend` impl provide construction, key prefixing, put/get/remove, and non-empty checks.

## Control Flow

Constructor parses endpoint, validates AWS role/web-identity/static credential combinations, requires bucket, builds static Signature V4 credentials, sets secure mode/region, extracts host, creates provider id `"s3"`, trims prefix, and stores storage class. Put promotes metadata and forces content MD5. Get applies version id and byte range. Remove applies version id. `in_use` lists one item under prefix.

## State and Persistence Behavior

Local state is client/config only. Remote S3 object versions are persisted and version ids are returned by put.

## Dependencies and Integration Points

Uses RustFS transition clients, credentials, get/put/remove options, URL parsing, shared metadata conversion, and path separator constants. Compatible provider wrappers embed and delegate to it.

## Risks and Edge Cases

AWS role/web identity paths are validated but not implemented as credential providers. Prefix joining is simple string concatenation. Endpoint path-style quirks depend on transition client.

## Test Signals

No direct tests; shared metadata tests exist in `warm_backend.rs`.
