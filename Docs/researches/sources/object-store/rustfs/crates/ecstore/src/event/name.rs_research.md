# sources/object-store/rustfs/crates/ecstore/src/event/name.rs

Purpose: This file preserves the legacy `rustfs_ecstore::event::name::EventName` path while moving the canonical event name definition to `rustfs_s3_types::EventName`.

Important APIs and types: The only public API is `pub use rustfs_s3_types::EventName`.

Control flow: There is no runtime behavior. The Rust compiler resolves imports through this re-export.

State and persistence behavior: The file has no state. Any serialization, parsing, or event-name compatibility behavior lives in `rustfs_s3_types::EventName`, not here.

Dependencies and integration points: Lifecycle and replication paths construct event names such as object-created, object-removed, lifecycle-expiration, and replication events through `EventName`. Keeping the old module path avoids a broad source migration while centralizing the enum in the shared S3 types crate.

Risks: This file can mask changes in the canonical type. If `rustfs_s3_types::EventName` changes variant names, serde behavior, or string formatting, ecstore callers observe that change through this compatibility path. There are no local guards here.

Test signals: There are no local tests. Build success of import sites and tests in `rustfs_s3_types` are the relevant signals.
