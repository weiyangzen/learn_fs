# sources/storage-engines/tikv/components/raftstore-v2/src/fsm/mod.rs

Purpose: Defines the FSM module facade for raftstore-v2. It documents the three FSM categories and re-exports the concrete types used by the batch system and other modules.

Important APIs/types/functions: The file declares `mod apply`, `mod peer`, and `mod store`. It re-exports `ApplyFsm`, `ApplyResReporter`, `ApplyScheduler`, `PeerFsm`, `PeerFsmDelegate`, `SenderFsmPair`, `Store`, `StoreFsm`, `StoreFsmDelegate`, and `StoreMeta`.

Control flow: No runtime control flow exists in this module. It is an organizational boundary.

State and persistence behavior: State behavior lives in the submodules. The documentation clarifies that `StoreFsm` handles global control/initialization, `PeerFsm` handles one raft peer, and `ApplyFsm` handles apply tasks for one peer.

Dependencies and integration points: `batch/store.rs`, operation modules, and crate public exports depend on these re-exports. It keeps the internal file layout hidden from callers.

Risks: Re-export churn affects import paths across raftstore-v2. The module categorization is important for maintainability because peer, store, and apply responsibilities are intentionally separated.

Test signals: Compile-time module coverage. Functional validation is in the submodules and integration tests.
