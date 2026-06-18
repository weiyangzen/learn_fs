# sources/object-store/rustfs/crates/protocols/src/swift/mod.rs

## Purpose
`mod.rs` is the Swift protocol module root. It documents the OpenStack Swift URL model, authentication expectations, and re-exports the shared router and error/result types.

## Important APIs, Types, And Functions
The file declares Swift submodules for account, ACL, bulk, container, CORS, DLO, encryption, errors, expiration, expiration worker, FormPost, handler, object, quota, ratelimit, router, SLO, static web, symlink, sync, TempURL, types, and versioning. It publicly re-exports `SwiftError`, `SwiftResult`, `SwiftRoute`, `SwiftRouter`, and selected type structs `Container`, `Object`, and `SwiftMetadata`.

## Control Flow
There is no runtime control flow in this file. Its role is compile-time organization and public API exposure for the protocols crate.

## State, Persistence, And Dependencies
No state is held here. The module-level docs describe the mapping `/v1/{account}/{container}/{object}`, where Swift containers map to S3 buckets and object names map to S3 keys. Authentication is described as Keystone token middleware storing credentials in task-local storage.

## Integration Points
Consumers import the Swift router/service/errors through this root. The breadth of declared modules shows the Swift implementation is intended to cover common compatibility features, but the root does not indicate maturity or whether a feature is wired into `handler.rs`.

## Risks And Test Signals
Because all feature modules are exported equally, scaffolded modules such as encryption, expiration worker, and ratelimit can look production-ready even when not integrated. The file has no tests; validation comes from compilation and downstream module tests.
