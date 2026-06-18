# sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/apply_trace.rs

## Purpose
Tracks apply persistence for raftstore-v2 tablets, where tablet WAL is disabled. It records data-CF flush progress and a virtual raft-CF admin progress so restart recovery can replay only the necessary raft logs without losing unflushed data or violating admin-operation barriers.

## Important APIs, Types, And Functions
`write_initial_states` writes bootstrap raft, apply, region, and flushed-index states. `StateStorage` adapts engine flush progress into raft-engine records and peer messages. `ApplyTrace` tracks per-CF `Progress`, admin progress, persisted apply index, explicit flush triggers, and ready-number flush tasks. Key methods include `recover`, `on_flush`, `on_modify`, `on_admin_flush`, `on_admin_modify`, `on_sst_ingested`, `should_flush`, `maybe_advance_admin_flushed`, `advance_flushed_index_for_ingest`, `log_recovery`, `restore_snapshot`, `on_applied_snapshot`, `should_persist`, `register_flush_task`, and `take_flush_index`. `Storage::new`, `recover_tablet`, `init_apply_trace`, and `record_apply_trace` connect trace state to storage lifecycle. Peer hooks include `on_data_flushed`, `on_data_modified`, `cleanup_stale_ssts`, and `flush_before_close`.

## Control Flow
Recovery reads persisted flushed indexes for all data CFs and the virtual raft CF, then loads region/apply state at the recovered admin index. During runtime, apply reports data modifications, engine flush callbacks report flushed indexes, and admin operations mark virtual raft-CF modifications/flushes. `maybe_advance_admin_flushed` advances the global safe replay point only when admin barriers are satisfied and unflushed data CFs permit it. Ingested SST ranges can bridge gaps beyond flush records. When `should_persist` is true, ready handling writes the raft-CF flushed index through the raft engine and records the ready number so stale SST cleanup can run after persistence completes.

## State And Persistence Behavior
Durable records include region state, apply state, raft state, and flushed indexes keyed by region, CF, tablet index, and apply index in the raft engine. In-memory `ApplyTrace` mirrors progress and decides when to persist. Snapshot restore resets modification markers without pretending data is flushed; applied snapshot marks all data/admin flushed. `flush_before_close` may force up to three oldest-CF flushes and synchronously persist the admin flushed index to reduce replay on shutdown.

## Dependencies And Integration Points
Depends on `KvEngine`/`RaftEngine` flushed-index APIs, tablet registry paths, encryption key manager, snapshot install paths, tablet worker cleanup tasks, flush state atomics, SST apply state, `PeerMsg::DataFlushed`, `WriteTask.extra_write`, and ready persistence callbacks.

## Risks And Edge Cases
Incorrect advancement of admin flushed index can cause data loss after restart or unnecessary replay. The code handles flush racing ahead of modification tracking by aligning impossible progress, treats SST ingests as pending inclusive ranges, and uses apply index rather than raw flushed index in `flush_before_close` to avoid advancing beyond seen modifications. Tablet recovery panics on missing tablet data after trying split and snapshot paths. Failpoints can force apply-trace persistence or reset apply index during restart.

## Test Signals
`test_write_initial_states` verifies bootstrap raft/apply/region/flushed records. `test_apply_trace` exercises data flush, admin barriers, and SST-ingest range advancement. `test_advance_admin_flushed` covers advancement edge cases, races, and non-regression. Failpoints include `should_persist_apply_trace`, `RESET_APPLY_INDEX_WHEN_RESTART`, and `flush_before_close_threshold`.
