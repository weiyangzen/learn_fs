# sources/storage-engines/tikv/components/raftstore-v2/src/router/mod.rs

Purpose: this module file defines the public router facade for raftstore-v2.

Important APIs/types/functions: it declares `imp`, `internal_message`, public `message`, and `response_channel` modules. It re-exports `RaftRouter`, `UnsafeRecoveryRouter`, `ApplyRes`, `SstApplyIndex`, `PeerMsg`, `PeerTick`, `RaftRequest`, `StoreMsg`, `StoreTick`, response-channel types, and `DiskSnapBackupHandle`. Test-only flush channel exports are gated by `testexport`.

Control flow: no runtime logic. It centralizes import paths for operation, FSM, and service layers.

State and persistence: none directly.

Dependencies/integration: consumers import router messages/channels through this facade rather than internal submodules.

Risks: export changes affect a broad compile surface. Keeping `ApplyTask` crate-private limits apply-worker internals.

Test signals: downstream compilation and module integration.
