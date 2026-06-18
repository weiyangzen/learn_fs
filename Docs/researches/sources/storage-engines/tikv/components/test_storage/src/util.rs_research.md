# Research: sources/storage-engines/tikv/components/test_storage/src/util.rs

## sources/storage-engines/tikv/components/test_storage/src/util.rs

Purpose: small utility module for constructing raft-backed storage fixtures. It exports macros for selecting leader/follower raft engines and functions that build `SyncTestStorage` from a running `test_raftstore::ServerCluster`.

Important APIs are `prepare_raft_engine!`, `leader_raft_engine!`, `follower_raft_engine!`, `new_raft_engine`, and `new_raft_storage_with_store_count`. The macros run the cluster if needed, force leader election with `must_get`, locate the region for a key, derive `Context` with region id, epoch, and peer, and return cloned `SimulateEngine` handles for leader or followers.

Control flow creates a new server cluster, runs it, extracts engine/context, and builds `SyncTestStorageBuilder::from_engine(engine).build(store_id)`. State and persistence are in the raft cluster and underlying engines; this module only picks handles and contexts.

Dependencies are `api_version::KvFormat`, `kvproto::Context`, `test_raftstore` cluster/server types, and `tikv_util::HandyRwLock`. Risks include using peer id vs store id carefully when indexing `storages`, assuming a leader is elected after `must_get`, and macro hygiene because the macros expand into caller scope. Test signals are downstream raft storage tests using leader/follower contexts to verify stale reads, leadership errors, and replicated storage behavior.
