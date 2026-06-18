# sources/storage-engines/tikv/components/resolved_ts/src/lib.rs

`lib.rs` is the crate facade for TiKV's resolved-ts component. Its module-level documentation states the core invariant: resolved-ts is a lower bound for future commit timestamps and an upper bound for commits already visible for transaction-level consistent views. It lists the required premises: track all region locks, use the minimum start-ts while locks exist, use a fresh timestamp when no locks exist, and advance only from the region leader after it has applied in its term.

The public API is mostly re-exported modules: `resolver`, `cmd`, `observer`, `advance`, `endpoint`, `errors`, `scanner`, and `metrics`. External users can construct observers and endpoints, schedule `Task`s, inspect or use `Resolver`, and consume metrics symbols through this facade. The crate enables `#![feature(box_patterns)]`, so it depends on nightly features in the TiKV build.

There is no runtime state in this file, but it defines the integration surface and makes internal modules part of the crate API. This has compatibility risk: broad `pub use` exports can expose internal types such as resolver internals or metrics names to other TiKV components. Test signals are distributed across module unit tests and integration tests that import `resolved_ts::Task`, metrics, and helpers directly.
