# sources/object-store/rustfs/crates/notify/Cargo.toml

Purpose: package manifest for `rustfs-notify`, the RustFS notification service crate that delivers real-time file/object events to configured targets.

Important APIs/types/functions: declares package metadata, workspace-managed edition/license/repository/rust-version/version/homepage, docs.rs documentation, keywords/categories, library doctests disabled, and Criterion bench `snapshot_mode_scan` with `harness = false`.

Control flow: Cargo uses this file to resolve build graph, features, benches, and lint inheritance. There is no runtime code.

State and persistence: no runtime state. Dependency choices indicate persisted/queued notification behavior through `rustfs-targets`, config models, and queue-related target configuration used in examples.

Dependencies/integration: internal crates include `rustfs-config` with notify/constants/server-config-model features, `rustfs-ecstore`, `rustfs-s3-types`, `rustfs-s3-ops`, `rustfs-targets`, and `rustfs-utils`. External dependencies include `arc-swap`, `async-trait`, `chrono`, `form_urlencoded`, `hashbrown`, `percent-encoding`, `rayon`, `rustc-hash`, serde, `starshard`, `thiserror`, Tokio, tracing, URL, `wildmatch`, metrics, and `quick-xml` with serialization/encoding features. Dev dependencies support Tokio tests, tracing subscriber, Axum examples, serde_json, time, and Criterion.

Risks: quick-xml compatibility is explicitly called out for custom S3 filter deserialization, so upgrading it may affect AWS XML compatibility. `tokio` is built with multi-thread runtime features. Disabling doctests means public examples in docs are not validated through `cargo test --doc`.

Test signals: `[[bench]] snapshot_mode_scan` is registered. Dev dependencies indicate async unit tests and webhook examples are expected to compile in test/example builds.
