# sources/storage-engines/tikv/components/raftstore-v2/src/batch/mod.rs

Purpose: Defines the raftstore-v2 batch-system module boundary. It states that store polling and apply execution use specialized batch systems.

Important APIs/types/functions: The file declares `mod store` and re-exports `StoreContext`, `StoreRouter`, `StoreSystem`, and `create_store_batch_system` from `store.rs`.

Control flow: There is no runtime control flow here. It is a module facade that keeps external users from depending on private batch implementation details while still exposing the core construction and routing types.

State and persistence behavior: State is implemented in `store.rs`; this file has no state.

Dependencies and integration points: It connects `lib.rs` public exports to the concrete store batch system. Other raftstore-v2 modules reference `crate::batch::StoreContext` for per-thread context shared across store and peer FSM delegates.

Risks: Re-export changes affect crate public API and internal imports. The module documentation distinguishes store and apply systems, but only store is declared here; apply FSM scheduling is built through `StorePollerBuilder` and `ApplyFsm`.

Test signals: Compile coverage validates exports. Behavioral tests target `store.rs` and higher-level raftstore-v2 integration suites.
