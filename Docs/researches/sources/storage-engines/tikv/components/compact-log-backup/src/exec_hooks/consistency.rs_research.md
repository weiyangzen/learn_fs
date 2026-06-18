# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/consistency.rs

Purpose: implements `StorageConsistencyGuard`, an execution hook that prevents compacting unstable log-backup data. It checks that the requested `until_ts` is not newer than a durable checkpoint, then acquires a remote read lock under `v1/LOCK` for the duration of the compaction.

Important APIs and types: `StorageConsistencyGuard`, internal `CheckpointSource`, `load_storage_checkpoint`, and `load_replication_status_checkpoint`. The default checkpoint source scans `v1/global_checkpoint/*.ts`, parses 8-byte little-endian timestamps, ignores malformed non-`.ts` files, and returns the maximum valid checkpoint. The replication-status source reads `<sub_prefix>/resume-state.json` and requires a numeric `last_checkpoint`.

Control flow: `before_execution_started` optionally loads a checkpoint, rejects `until_ts > checkpoint`, warns and fails when no storage checkpoint exists, then calls `lock_for_read`. `after_execution_finished` unlocks. `on_aborted` also unlocks and logs unlock failures.

State and persistence: persists no new data except the external-storage lock record; it depends on checkpoint objects written by backup-stream components. Lock cleanup is critical because a stale lock can block writers or later compaction attempts.

Dependencies and integration: uses `ExternalStorage`, external-storage locking, `ExecHooks`, `ExecutionConfig`, `ErrorKind`, and `storage_url`. `execute::load_until_ts_from_checkpoint` delegates checkpoint loading here.

Risks: checkpoint JSON schema errors are fatal; malformed storage checkpoint files are ignored, so a deployment with only malformed `.ts` files behaves like no checkpoint. Lock release is best effort on abort, so operator cleanup may be needed after external-storage failures.

Test signals: execution tests cover checkpoint bound rejection/acceptance, lock presence during execution, lock release after success, and unlock-on-abort behavior.
