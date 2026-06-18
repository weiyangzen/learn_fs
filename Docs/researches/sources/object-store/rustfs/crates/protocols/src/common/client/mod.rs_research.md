# sources/object-store/rustfs/crates/protocols/src/common/client/mod.rs

## Purpose

Defines the common client module boundary for protocol code and re-exports the S3 storage backend trait under a protocol-neutral alias.

## Important APIs, Types, and Functions

- `pub mod s3;` exposes the S3 client backend module.
- `pub use s3::StorageBackend as S3StorageBackend;` re-exports the trait for callers that want a clear S3-specific backend interface.

## Control Flow

No runtime control flow. This file is module wiring.

## State and Persistence

No state or persistence.

## Dependencies and Integration Points

Integrates `common::client::s3` with the rest of the protocols crate. Consumers can import `S3StorageBackend` from the common client module instead of the nested S3 module.

## Risks and Edge Cases

Any future backend traits added here should avoid name collisions and preserve the existing re-export path for downstream code.

## Test Signals

No local tests; compile tests and downstream use validate this module boundary.
