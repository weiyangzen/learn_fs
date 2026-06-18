# sources/storage-engines/tikv/components/engine_panic/src/lib.rs

Purpose: Crate root for the panic engine skeleton. It exports modules that mirror the full TiKV engine trait layout.

Important APIs and types: Re-exports include CF names/options, compaction, DB options, DB vectors, engine, import, misc, snapshot, SST, write batch, range/MVCC/TTL properties, perf context, flow control, table properties, and checkpoint modules. `raft_engine` is private but provides trait impls for `PanicEngine`.

Control flow and state: No runtime logic beyond module wiring. The crate has `#![allow(unused)]` because it is a template.

Dependencies and integration: Intended for new engine implementors to copy and replace `Panic*` types with real implementations. It keeps module organization aligned with other TiKV engines.

Risks: Publicly exported panic types can be instantiated and then panic on use. The skeleton should not be used as a functional engine.

Test signals: Compile-time conformance across the crate is the primary signal.
