# sources/storage-engines/tikv/components/tidb_query_common/src/lib.rs

Purpose: crate root for common TiDB query utilities. It enables min specialization and exposes modules for macros, errors, execution stats, metrics, storage, and utility helpers.

Important APIs and control flow: exports `macros`, `error`, `execute_stats`, `metrics`, `storage`, and `util`, and re-exports `Error` and `Result` from `error.rs` for convenient downstream use.

State and persistence behavior: no runtime state; module wiring only.

Dependencies and integration: downstream query crates import `tidb_query_common::{Result, Error}` and use exported modules for storage scans, metrics recording, and stats.

Risks and test signals: the crate requires nightly `min_specialization`, matching the specialized conversion/update patterns used by query components. Any module visibility changes are broad API changes.
