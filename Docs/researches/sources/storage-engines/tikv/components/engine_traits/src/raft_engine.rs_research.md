# sources/storage-engines/tikv/components/engine_traits/src/raft_engine.rs

Purpose: Defines generic Raft log/state storage traits used alongside the KV engine.

Important APIs and control flow: `RaftEngineReadOnly` exposes store/bootstrap state, raft state, region/apply state by apply index, flushed index, dirty mark, recover state, single entry, and ranged entry fetch. `RaftEngineDebug` scans/dumps all entries and states. `RaftEngine` creates log batches, syncs, consumes batches, cleans/gcs logs, prunes old states, supports manual purge, metrics, stop, stats/size/path, and raft-group iteration. `RaftLogBatch` appends entries, writes store/region/apply/raft/recover/flushed/dirty state, reports persist size, emptiness, and merging.

State, persistence, and dependencies: This is durable Raft metadata and log storage, including per-region states and flushed-index records used by KV flush recovery. Dependencies include `kvproto` raft server messages and `raft::eraftpb::Entry`.

Integration points, risks, and test signals: Used by raftstore, recovery, log GC, and `flush.rs` persistence. Risks include apply-index lookup semantics, overwrite/delete ranges in append, large GC batching, manual purge defaults, and error conversion to Raft. Signals come from Raft engine backend tests and recovery tests.
