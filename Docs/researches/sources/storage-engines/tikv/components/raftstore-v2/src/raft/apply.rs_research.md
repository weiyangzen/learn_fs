# sources/storage-engines/tikv/components/raftstore-v2/src/raft/apply.rs

Purpose: this file defines the raftstore-v2 apply-side state object that applies committed raft commands to a tablet and reports apply results.

Important APIs/types/functions: `Observe` tracks coprocessor observation info. `Apply<EK, R>` contains peer identity, current tablet, write batch, region state, apply progress, data-modification trace, callback queue, apply flow control, flush/SST state, log recovery trace, schedulers, importer, coprocessor host, metrics, logger, and bucket stats. Methods are mostly accessors and state mutators: `new`, `ensure_write_buffer`, `set_apply_progress`, `apply_progress`, `set_tablet`, callback/admin-result handling, `release_memory`, trace and flow-control accessors, and scheduler/importer accessors.

Control flow: construction loads the latest tablet from `TabletRegistry`, derives current applied index from `FlushState`, initializes perf context, and rejects `use_delete_range` for v2. Applying command logic lives in other operation files, but those paths mutate this structure as the single apply FSM state. `set_apply_progress` also clears `log_recovery` once all CF replay targets are reached.

State and persistence: `Apply` buffers writes in an engine write batch and tracks modifications separately from `flush_state`; comments emphasize that apply progress is updated after each command, but flush state must not be advanced immediately because manual flushes from other threads could observe an incorrect index. `sst_apply_state` and `sst_applied_index` coordinate SST ingestion visibility.

Dependencies/integration: integrates with engine traits, `TabletRegistry`, raftstore apply metrics/config, coprocessor observation, SST importer, tablet worker, read scheduler, and result reporter. Snapshot generation in `snapshot.rs` uses `apply_progress`, `flush`, tablet clone, and read scheduler.

Risks: exposing a new tablet before pending write batch is empty would mismatch tablet content and epoch, so `set_tablet` asserts an empty batch. Incorrect modification tracing can let raft logs be deleted before CF data is flushed. Log recovery depends on per-CF indexes being accurate.

Test signals: direct tests are not in this file, but snapshot/storage tests construct `Apply::new` and exercise snapshot scheduling.
