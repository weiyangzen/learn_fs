# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/save_meta.rs

Purpose: persists compact-log-backup output metadata. It writes batched subcompaction metadata under the compaction artifact prefix and emits a final BR-readable migration describing generated SSTs and metadata edits.

Important APIs and types: `SaveMeta`, `BatchConfig`, `MetaBatchWriter`, `CheckpointInput`, `CheckpointedSubcompaction`, `load_checkpointed_subcompactions`, and `final_artifacts_prefix`. `CheckpointedSubcompaction` canonicalizes source spans by sorting inputs, allowing checkpoint hooks to compare completed work independent of ordering.

Control flow: `before_execution_started` initializes run metadata, artifact paths, generated SST path, and the batch writer. `before_a_subcompaction_start` accumulates load/collection stats. `after_a_subcompaction_end` adds the result to `CompactionRunInfoBuilder`, updates stats, and appends the `LogFileSubcompaction` proto to the batch writer; the writer flushes when either subcompaction count or encoded bytes exceeds configured limits. `on_subcompaction_skipped` preserves already-done subcompactions in the collector. `after_execution_finished` flushes pending batches, adds JSON comments, and writes the migration.

State and persistence: writes `metas/batch_<run_uuid>_<seq>.cmeta` files and a migration under `v1/migrations`. It reads existing `.cmeta` batches for checkpoint recovery, ignoring corrupt or unreadable batches with warnings.

Dependencies and integration: integrates with `ExecHooks`, `CompactionRunInfoBuilder`, `MigrationStorageWrapper`, protobuf, `ExternalStorage`, retry wrappers, and UUIDs. It is essential for real restore because raw SST outputs alone are insufficient.

Risks: final migration write is the commit point; `.cmeta` batches from failed attempts can remain and are intentionally reused by checkpointing. Corrupt checkpoint batches are ignored, so partial external-storage corruption can cause re-execution. The writer must be initialized before subcompactions finish or it returns an explicit error.

Test signals: execution tests validate simple migration output, batched checkpoint reuse across failed attempts, small-compaction skipping persistence, and migration contents.
