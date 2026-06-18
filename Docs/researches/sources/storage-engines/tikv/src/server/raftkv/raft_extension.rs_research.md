# sources/storage-engines/tikv/src/server/raftkv/raft_extension.rs

Purpose: adapts a legacy raftstore router to `tikv_kv::RaftExtension` for transport, debug, split, and query operations. `RaftRouterWrap<S, E>` derefs to the underlying router while implementing the extension trait.

Important APIs/types/functions: `RaftRouterWrap::new`; `Deref`/`DerefMut`; `feed`; reachability/snapshot/resolved report methods; `split`; `query_region`; `check_consistency`.

Control flow: `feed` sends inbound raft messages and logs failures only for key messages. `split` sends `CasualMessage::SplitRegion`, waits for a paired write callback, validates raft command response, and returns generated regions. `query_region` sends `AccessPeer` and returns `RegionMeta`. `check_consistency` queries meta, verifies leader role, finds the leader peer, and sends `ComputeHash` admin command.

State/persistence: wrapper has no durable state; forwarded raftstore/admin commands drive actual raftstore persistence or in-memory raft state.

Dependencies/integration: `RaftStoreRouter`, `CasualMessage`, `RegionMeta`, `RaftStateRole`, `SnapshotStatus`, paired futures, and `raftkv::exec_admin`. Risks include silent non-key feed drops, callback cancellation, and `leader.unwrap()` assuming leader id is present in peers after role check. No local tests; covered indirectly by server/raftstore integration.
