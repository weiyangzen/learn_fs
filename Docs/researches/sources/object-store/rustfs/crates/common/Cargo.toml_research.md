# sources/object-store/rustfs/crates/common/Cargo.toml

## Purpose
This manifest defines the `rustfs-common` crate, a shared utility/data-structure crate for RustFS. It packages global state helpers, healing channel DTOs and messaging, last-minute metrics helpers, readiness exports, and other common modules.

## Important APIs, Types, and Functions
The crate uses workspace metadata and lints, disables doctests, and depends on `tokio`, `tonic`, `uuid`, `chrono`, `metrics`, `serde`, `rmp-serde`, `s3s`, and `tracing`. These dependencies correspond to async global locks/channels, gRPC channels, IDs, timestamps, serialization, S3 lifecycle/replication DTOs, and logging.

## Control Flow
No runtime flow is in the manifest. Dependency selection enables the code paths in `globals.rs`, `heal_channel.rs`, `last_minute.rs`, and exported readiness/metrics modules.

## State and Persistence Behavior
The manifest does not configure persistence. The crate's stateful behavior is process-global in code via `LazyLock`, `OnceLock`, async locks, atomics, and channels.

## Dependencies and Integration Points
`rustfs-common` is a foundational internal crate. Its dependencies suggest integration with server startup/readiness, cluster gRPC clients, S3 admin/heal logic, lifecycle/replication rules, and metrics reporting.

## Risks and Edge Cases
Because this crate carries global state utilities, dependency or API changes can have broad workspace impact. The `rmp-serde` and `metrics` dependencies are not visible in the researched files but likely support other modules not in this subset.

## Test Signals
Tests in researched modules validate heal channel labels/broadcasting and last-minute metric math. Manifest-level health depends on workspace dependency compatibility.
