<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raft_engine.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/raft_engine.rs

Purpose: implements raft-engine traits over RocksDB for legacy/default raft log persistence.

Important APIs/types/functions: `RaftEngineReadOnly`, `RaftEngineDebug`, `RaftEngine`, and `RaftLogBatch` impls for `RocksEngine`/`RocksWriteBatchVec`; private `gc_impl` and `append_impl`.

Control flow: small raft log fetches use point gets; larger fetches scan key ranges, validate indexes, respect `max_size`, and distinguish compacted vs unavailable entries. Batches append serialized entries, optionally delete overwritten gaps, persist raft/store/bootstrap/recover state, consume with optional sync, clean group data, and iterate region states.

State and persistence behavior: stores raft logs and metadata in default CF under raft key encodings; writes flow through Rocks write batches and WAL sync according to caller options.

Dependencies/integration: ties `keys`, protobuf raft/kvproto messages, `engine_traits::RaftEngine`, and Rocks write batches together.

Risks: raftstore-v2-only methods intentionally panic because this backend is not used for them. Fetch logic asserts strict sequential indexes and returns compacted/unavailable errors based on gaps.

Test signals: no local tests in this file; covered by raftstore and engine trait integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/raft_engine.rs -->
