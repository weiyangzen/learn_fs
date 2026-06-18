# sources/storage-engines/tikv/components/compact-log-backup/src/lib.rs

Purpose: crate root for the compact-log-backup component. It wires internal modules, public modules, feature gates, and public error/config exports.

Important APIs and types: public modules `test_util`, `exec_hooks`, and `execute`; re-exports `Error`, `ErrorKind`, `OtherErrExt`, `Result`, `TraceResultExt`, and `execute::ShardConfig`. Internal modules include `cache`, `compaction`, `errors`, `source`, `statistic`, `storage`, and `util`.

Control flow: no runtime flow in this file. It defines visibility boundaries: execution and hooks are exposed, while storage/source/statistic internals remain crate-private except through public APIs and test utilities.

State and persistence: none directly. Persistence functionality is rooted in `storage`, `source`, and `exec_hooks::save_meta`.

Dependencies and integration: enables nightly features `test` and `custom_test_frameworks`, indicating benchmark/test infrastructure depends on unstable Rust. The public surface is consumed by TiKV tooling or tests that run compact-log-backup.

Risks: exposing `test_util` publicly behind `#![cfg(test)]` content in the file itself can be confusing; consumers only see it in test builds. The crate root does not expose most low-level storage types, so external callers should use `execute` and hook modules rather than bypass internals.

Test signals: module-level tests are spread across the internal modules; this root’s main validation is successful crate compilation and test discovery with the enabled nightly features.
