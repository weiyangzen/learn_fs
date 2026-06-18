# sources/storage-engines/tikv/components/raftstore/src/store/fsm/mod.rs

## Purpose

`sources/storage-engines/tikv/components/raftstore/src/store/fsm/mod.rs` is the module root and public facade for the raftstore finite state machine implementation. It defines the FSM submodules and re-exports the primary types and constructors used by the rest of the raftstore crate.

The file was read completely as a 25-line Rust module. Its documentation explains the current architecture: peers are state machines representing region replicas, while the store is also a special state machine for store-wide requests; the two are still mixed but expected to separate in the future.

## Important APIs, Types, and Functions

Declared submodules are `apply`, `life`, `metrics`, `peer`, and `store`. `apply`, `life`, and `store` are public modules; `metrics` and `peer` are private modules with selected public re-exports.

The apply facade re-exports `Apply`, `ApplyBatchSystem`, `ApplyMetrics`, `ApplyRes`, `ApplyRouter`, `ApplyPollerBuilder`, `CatchUpLogs`, `ChangeObserver`, `ChangePeer`, `ExecResult`, `GenSnapTask`, `ApplyTask`, `ApplyNotifier`, `Proposal`, `Registration`, `SwitchWitness`, `ApplyTaskRes`, `check_sst_for_ingestion`, and `create_apply_batch_system`.

The metrics facade re-exports `GlobalStoreStat` and `LocalStoreStat`.

The peer facade re-exports `DestroyPeerJob`, `MAX_PROPOSAL_SIZE_RATIO`, `PeerFsm`, `new_admin_request`, and `new_read_index_request`.

The store facade re-exports `RaftBatchSystem`, `RaftPollerBuilder`, `RaftRouter`, `StoreMeta`, and `create_raft_batch_system`.

## Control Flow

There is no runtime control flow in this file. Its effect is compile-time namespace wiring: external modules import raftstore FSM capabilities through `crate::store::fsm::*` or selected nested modules instead of depending directly on every implementation file.

The facade matters operationally because it shapes construction flow elsewhere. Store startup uses `RaftPollerBuilder` and `create_raft_batch_system`; apply startup uses `ApplyPollerBuilder` and `create_apply_batch_system`; routers and task/result types cross the boundaries between store FSM, peer FSM, apply FSM, workers, and transport.

## State and Persistence Behavior

`mod.rs` owns no state and performs no persistence. It exposes state-bearing types from submodules, especially `StoreMeta`, `PeerFsm`, `Apply`, `GlobalStoreStat`, and `LocalStoreStat`. Persistence behavior remains in the re-exported implementation modules, particularly apply, peer storage, and store FSM code.

## Dependencies and Integration Points

The direct dependencies are its sibling modules. Broader integration points include `store/mod.rs`, `router.rs`, async I/O write routing, peer storage, workers, unsafe recovery, read queues, split checks, and tests that import the public raftstore FSM surface.

Because `life` is public as a module while `metrics` and `peer` are private with curated re-exports, this file also encodes intended API boundaries. Compatibility helpers in `life.rs` can be used by both raftstore variants, while peer internals remain mostly hidden.

## Risks and Edge Cases

Re-export changes are source-compatibility changes for the rest of the crate and potentially downstream crates if this module is part of a public crate API. Removing or renaming an item here can break imports far from the implementation file.

The facade can hide ownership boundaries: many high-level types are exported from one place even though they belong to different subsystems. That matches current raftstore architecture, but broadening this file further can increase coupling between apply, peer, and store FSMs.

Module visibility is intentional. Making `metrics` or `peer` public wholesale would expose implementation details; hiding `life` would break shared lifetime-management use cases.

## Test Signals

Compile tests are the primary signal: imports through `crate::store::fsm` should continue to resolve for store startup, apply batch systems, routers, unsafe recovery, and worker integrations.

Refactors to this file should run raftstore unit tests or at least targeted checks covering creation of raft and apply batch systems, peer/admin/read-index request constructors, and code paths importing `GlobalStoreStat` / `LocalStoreStat`.

A useful review signal is import churn: if many callers need to switch from facade imports to deep module paths, the facade may no longer be serving its stabilizing role.
