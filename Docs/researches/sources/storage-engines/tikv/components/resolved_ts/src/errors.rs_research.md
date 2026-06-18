# sources/storage-engines/tikv/components/resolved_ts/src/errors.rs

This small module defines the resolved-ts component error boundary. `Error` has two variants: `MemoryQuotaExceeded`, wrapping `tikv_util::memory::MemoryQuotaExceeded`, and `Other`, wrapping a boxed `dyn std::error::Error + Sync + Send`. The module also defines `Result<T>` as the component-local result alias.

The purpose is to keep quota failures distinguishable from generic operational failures. `endpoint.rs` matches `Error::MemoryQuotaExceeded` to re-register all regions and shed accumulated pending memory, while `Error::Other` usually re-registers only the affected region. `scanner.rs` converts raftstore snapshot and MVCC scan failures into `Error::Other`, while pending and resolver lock tracking use the quota variant.

There is no persistent state here. The integration point is Rust's `thiserror::Error` derive and `From` conversions, which keep call sites concise with `?` and `box_err!`. The main risk is overuse of `Other`, which can erase structured raftstore causes such as epoch mismatch except where the caller parses them first. Test coverage is indirect through scanner and endpoint failpoint tests that assert distinct quota and re-registration behavior.
