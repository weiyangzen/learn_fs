# sources/object-store/rustfs/crates/ecstore/src/bucket/versioning_sys.rs

## Purpose
`BucketVersioningSys` is the async access facade for bucket versioning configuration. It reads bucket metadata and exposes convenient boolean checks for enabled/suspended state.

## Important APIs, Types, and Functions
- `BucketVersioningSys::new` and `Default` construct the empty facade.
- `enabled`, `prefix_enabled`, `suspended`, and `prefix_suspended` call `get` and return false on errors after logging.
- `get(bucket)` returns a default `VersioningConfiguration` for internal metadata buckets, otherwise locks the global bucket metadata system and calls `get_versioning_config`.

## Control Flow and State Behavior
All public checks are async static methods. They centralize error-to-false fallback, which keeps callers simple but hides metadata failures. `get` obtains the metadata system with `get_bucket_metadata_sys`, takes a write lock, fetches config and ignores the second tuple element.

## Dependencies and Integration Points
It depends on `metadata_sys::get_bucket_metadata_sys`, `VersioningApi`, `RUSTFS_META_BUCKET`, crate `Result`, S3 DTOs, and tracing warnings. It is an integration point between bucket metadata persistence and object operation policy decisions.

## Persistence
This file does not persist itself; it reads persisted bucket metadata via the metadata subsystem. Internal metadata buckets are treated as unversioned/default without hitting metadata storage.

## Risks and Edge Cases
Error fallback to false may make transient metadata-store failures look like disabled versioning. `bucket.starts_with(RUSTFS_META_BUCKET)` treats any bucket with that prefix as internal. The metadata system is acquired with a write lock even though this path appears read-only, which may reduce concurrency.

## Test Signals
No inline tests. Useful tests would mock metadata config fetches, metadata errors, internal bucket bypass, and prefix-specific delegated behavior.
