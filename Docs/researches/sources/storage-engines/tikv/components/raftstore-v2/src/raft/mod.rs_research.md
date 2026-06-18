# sources/storage-engines/tikv/components/raftstore-v2/src/raft/mod.rs

Purpose: this is the public module facade for raftstore-v2 raft wrapper types.

Important APIs/types/functions: it declares submodules `apply`, `peer`, and `storage`, then re-exports `Apply`, `Peer`, and `Storage`.

Control flow: no runtime control flow exists here. It defines the module boundary used by operation/router/FSM code.

State and persistence: none directly. The re-exported types own apply state, peer orchestration state, and raft storage persistence state.

Dependencies/integration: external code imports `crate::raft::{Apply, Peer, Storage}` through this module, avoiding direct submodule paths.

Risks: minimal; changing exports would ripple through many operation files.

Test signals: no tests needed beyond downstream compilation.
