# sources/storage-engines/tikv/components/resource_control/Cargo.toml

This manifest defines the `resource_control` crate, an unpublished Apache-2.0 TiKV component using Rust edition 2024. It exposes one optional feature, `failpoints`, mapped to `fail/failpoints`, which enables failpoint-driven tests in the future limiter path.

Dependencies show the crate's integration surface: `pd_client` and `kvproto` for resource-group metadata and RPCs, `tikv_util` for resource-control primitives and workers, `file_system` for IO byte accounting, `futures` and `tokio-timer` for async throttling, `crossbeam` and priority queues for channels, `online_config` and `serde` for dynamic configuration, `prometheus` for metrics, and `yatp` for pool integration. Dev dependencies include `test_pd`, `rand`, and test-exported `file_system`.

There is no runtime control flow in the manifest, but it is a risk signal: `yatp` is pulled from a Git branch rather than a versioned crate, and `dashmap` is pinned directly while most dependencies use workspace versions. Build/test behavior depends on nightly features used by the crate source and on feature-gated failpoints for some tests.
