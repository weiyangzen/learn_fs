# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_rustfs.rs

## Purpose

RustFS-to-RustFS warm-tier adapter using the transition-client S3-compatible API.

## Important APIs and Types

`WarmBackendRustFS(WarmBackendS3)`, constructor, `WarmBackend` impl, multipart constants/helper, and an endpoint-host regression test.

## Control Flow

Validates credentials/bucket, parses endpoint, rejects missing host, creates Signature V4 credentials with trailing headers, builds provider id `"rustfs"`, wraps S3 backend, uploads with computed part size and disabled content SHA256, and delegates read/remove/in-use.

## State and Persistence Behavior

Only client/config in memory; remote RustFS bucket/prefix persists tiered objects.

## Dependencies and Integration Points

Uses `TierRustFS`, transition API types, `WarmBackendS3`, and shared metadata conversion. Also participates in extended tier migration via `tier.rs` hints.

## Risks and Edge Cases

Relies on S3-compatible semantics between RustFS clusters. `tier` is unused. SHA256 disabling and fixed multipart thresholds need compatibility validation.

## Test Signals

Test verifies missing-host endpoint returns an error rather than panicking. More CRUD and metadata tests are needed.
