# sources/storage-engines/tikv/components/engine_panic/src/raft_engine.rs

Purpose: Panic skeleton for raft log engine traits using `PanicEngine` and `PanicWriteBatch`.

Important APIs and types: `PanicEngine` implements `RaftEngineReadOnly`, `RaftEngineDebug`, and `RaftEngine`. `PanicWriteBatch` implements `RaftLogBatch`. Methods cover raft state, entries, store ident, bootstrap region, region/apply state, flushed index, dirty mark, recover state, scans, batch creation/consume, log cleanup, GC, purge, metrics, size/path, raft-group iteration, and batch mutations.

Control flow and state: All methods panic. No raft log state, batches, or persistence exists.

Dependencies and integration: Depends on `kvproto` raft/server metadata, `raft::eraftpb::Entry`, and `engine_traits` raft traits. It documents the full raft-engine surface expected by TiKV.

Risks: Runtime use panics; this module is private from crate root but its trait implementations attach to exported types.

Test signals: No tests.
