# sources/storage-engines/tikv/components/raft_log_engine/src/engine.rs

Purpose: Implements TiKV's `engine_traits` raft engine traits on top of `raft_engine::Engine`, including encrypted/rate-limited filesystem wrappers, raft log batches, raft state metadata, apply/region/flush state storage, compaction, manual purge, and debug scanning.

Important APIs/types/functions: `MessageExtTyped` tells raft-engine how to read `raft::eraftpb::Entry` indexes. `ManagedReader`, `ManagedWriter`, `ManagedFileSystem`, and `ManagedHandle` wrap `DefaultFileSystem` with optional `DataKeyManager` encryption metadata and `IoRateLimiter` throttling. `RaftLogEngine::new`, `exists`, `raft_groups`, `first_index`, and `last_index` wrap the raw engine. `RaftLogBatch` implements `RaftLogBatchTrait` with `append`, state puts, flushed-index records, dirty marks, and recover-state writes. `RaftEngineReadOnly`, `RaftEngineDebug`, and `RaftEngine` impls expose reads, scans, writes, clean/gc, state cleanup, purge, size, and group iteration. `transfer_error` maps raft-engine errors to TiKV engine errors.

Control flow: Writes are staged in `LogBatch` commands and committed through `consume`/`consume_and_shrink` with foreground-write I/O type. State keys are encoded with one-byte prefixes plus big-endian numeric suffixes. Reads for region/apply state scan backwards from a prefix range to find the newest state at or before an apply index. `delete_all_but_one_states_before` scans state records and deletes older duplicates while preserving one record per state kind/CF.

State and persistence behavior: Raft logs and TiKV raftstore metadata are persisted in raft-engine namespaces keyed by raft group id. Store-wide metadata uses raft group id `0`. Encryption metadata is created, linked, rotated, or deleted alongside file create/rename/reuse/delete operations. Manual purge is required and delegates to raft-engine expired-file purge.

Dependencies and integration points: It depends on `engine_traits`, `raft_engine`, `kvproto` raft server protos, encryption, file-system rate limiting, and TiKV logging. Raftstore-v2 uses this engine through generic `RaftEngine` bounds for append, apply-state persistence, compact-log GC, and bootstrap store identity.

Risks: Key-prefix ordering is critical for scans and cleanup; debug assertions guard some assumptions. Path conversion uses `to_str().unwrap()`, so non-UTF8 paths would panic. `cf_to_id` panics for unknown column families. Encryption rename/reuse metadata rollback paths log failures but must remain consistent to prevent unreadable files. `exists` unwraps `read_dir`.

Test signals: Local `test_apply_related_states` verifies initial absence, state/flushed-index writes, reverse lookup by apply index, and latest flushed-index behavior. Additional integration should cover encryption metadata, GC, manual purge, entry fetch, dirty marks, and recovery state.
