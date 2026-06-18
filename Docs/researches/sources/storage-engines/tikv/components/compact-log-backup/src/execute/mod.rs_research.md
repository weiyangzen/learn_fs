# sources/storage-engines/tikv/components/compact-log-backup/src/execute/mod.rs

Purpose: orchestrates compact-log-backup execution: external-storage setup, metadata discovery, subcompaction collection, bounded concurrent SST compaction, hook calls, abort handling, sharding, and checkpoint loading.

Important APIs and types: `create_storage_with_gcp_v2`, `load_until_ts_from_checkpoint`, `ShardConfig`, `parse_shard_config`, `ExecutionConfig`, and `Execution<DB>`. `ShardConfig` hashes store IDs with CRC64 and exposes a stable suffix for output prefixes. `ExecutionConfig::recommended_prefix` hashes operational inputs to produce deterministic artifact prefixes.

Control flow: `run_with_storage_async` wraps `run_prepared` in Ctrl-C abort handling. `run_prepared` counts metadata, updates `shift_ts`, calls `before_execution_started`, streams metadata through `StreamMetaStorage`, collects subcompactions either from logical log files or cached physical files, lets hooks skip work, spawns `SubcompactionExec` tasks up to `max_concurrent_subcompaction`, verifies checksums, drains pending tasks, and calls `after_execution_finished`. Scheduling errors abort and drain all pending tasks.

State and persistence: this module coordinates persistence but writes through lower layers and hooks. Output paths are rooted at `out_prefix`; optional `PhysicalFileCache` stores raw physical files in memory during execution.

Dependencies and integration: depends on `compaction` collectors/executor, `storage::StreamMetaStorage`, `cache::PhysicalFileCache`, hook traits, Tokio, tracing-active-tree, `ExternalStorage`, Rocks SST traits, and BR storage protobufs.

Risks: `tokio::spawn(...).await.unwrap()` in metadata prefetch assumes spawned metadata tasks do not panic. Concurrent hook side effects can fail the whole run. Shard filtering requires parseable backupmeta names only in shard mode. `shift_ts` can be derived from metadata names and affects default-CF compaction selection.

Test signals: `execute/test.rs` covers simple execution, checkpoint reuse, consistency locks, sharding validation/union behavior, small-skip behavior, and migration output.
