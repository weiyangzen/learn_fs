# sources/storage-engines/tikv/components/tidb_query_common/Cargo.toml

Purpose: declares the shared `tidb_query_common` crate for TiDB pushed-down executor utilities.

Important APIs and control flow: package metadata marks it non-published and Rust 2021. Dependencies cover errors (`anyhow`, `thiserror`, `error_code`), async traits/futures, protobufs, metrics, tracker integration, logging wrappers, API version support, and scheduling/runtime helpers.

State and persistence behavior: no runtime state in the manifest. It defines build-time dependency boundaries for error handling, statistics, storage abstraction, and metrics modules.

Dependencies and integration: used by query expression, aggregate, and executor crates for `Result`, storage traits, execution summaries, and metrics. Dev dependency `byteorder` supports storage range tests.

Risks and test signals: workspace dependency versions and nightly prometheus feature choices affect downstream compatibility. Manifest itself is validated by Cargo builds.
