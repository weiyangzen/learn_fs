# sources/storage-engines/tikv/components/engine_rocks/src/checkpoint.rs

Purpose: Implements RocksDB checkpoint creation and instance merge for `RocksEngine`.

Important APIs and types: `RocksEngine` implements `Checkpointable` with associated `RocksEngineCheckpointer`. `RocksEngineCheckpointer` wraps `rocksdb::Checkpointer` and implements `create_at`.

Control flow: `new_checkpointer` delegates to RocksDB and maps errors. `merge` creates `MergeInstanceOptions` with `merge_memtable=false` and `allow_source_write=true`, collects raw inner DB references, and calls RocksDB `merge_instances`. `create_at` optionally deletes the output directory in test builds, then delegates to RocksDB with optional Titan output and log-size flush threshold.

State and persistence behavior: Checkpoints materialize RocksDB state at output directories. Merge mutates the target DB by merging source instances while allowing source writes.

Dependencies and integration: Used by backup/snapshot/admin flows that need consistent engine checkpoints. Integrates `file_system` cleanup in tests and RocksDB checkpoint APIs.

Risks: Creating a checkpoint while background work is paused can fail, as the test expects. Test-only deletion of output directories must remain behind cfg. Merge options intentionally do not merge memtables, so callers must understand durability/flush requirements.

Test signals: `test_checkpoint` writes a key, verifies checkpoint failure while background work is paused, resumes background work, creates a checkpoint, opens it, and reads the key.
