# sources/storage-engines/tikv/components/compact-log-backup/src/execute/test.rs

Purpose: integration-style test suite for compact-log-backup execution, hooks, checkpointing, consistency locks, sharding, and metadata persistence.

Important APIs and helpers: `CompactionSpy`, `create_compaction`, `gen_builder`, `gen_store_builders`, `store_paths`, `populate_stores`, `run_exec`, `run_exec_err`, `set_metadata_store_id`, `load_migrations_by_out_prefix`, and `meta_edits_by_path`.

Control flow: tests build temporary external storage with synthetic log-backup metadata, run `Execution` in blocking tasks, receive completed `SubcompactionResult`s through channels, verify generated SST contents via `TmpStorage::verify_result`, and inspect migrations and `.cmeta` batches. The checkpoint test intentionally fails multiple attempts after a fixed number of completed subcompactions, then confirms that only committed batches are reused on a final successful run.

State and persistence: writes local-storage metadata/log files, checkpoint files, lock files, subcompaction metadata batches, and migration files. Helpers rewrite metadata store IDs to test shard safety.

Dependencies and integration: exercises `SaveMeta`, `Checkpoint`, `StorageConsistencyGuard`, `SkipSmallCompaction`, `SubcompactionExec`, `ExternalStorage`, BR protobuf metadata, and sharding config.

Risks covered: checkpoint boundary enforcement, stale lock cleanup on abort, skipped compaction persistence semantics, invalid backupmeta names in shard mode, path/metadata store-ID mismatches, and equivalence between unioned shard migrations and unsharded migration output.

Test signals: this file is itself the strongest signal for the execution stack. It validates both behavioral output and persistence artifacts, not just function-level return values.
