# sources/object-store/rustfs/crates/ecstore/src/disk/disk_store.rs

## Purpose
`disk_store.rs` wraps a concrete local disk implementation with health tracking, stale disk-id checks, timeout policy, active monitoring, recovery probing, and `DiskAPI` delegation. It is the local-drive equivalent of the remote disk health boundary used by RPC disks, and it is intentionally stateful: every operation can update health state, waiting-operation metrics, and recovery state.

## Important APIs, Types, And Functions
- `DriveTimeoutProfile` and `TimeoutHealthPolicy` parse env-backed timeout behavior. The profile chooses default versus high-latency timeout defaults; the health policy controls whether scanner/listing timeouts mark a drive unhealthy.
- `get_max_timeout_duration`, `get_drive_metadata_timeout`, `get_drive_disk_info_timeout`, `get_drive_list_dir_timeout`, `get_drive_walkdir_timeout`, `get_drive_walkdir_stall_timeout`, `get_drive_active_check_interval`, and `get_drive_active_check_timeout` centralize disk timeout configuration via `rustfs_config` and `rustfs_utils`.
- `DiskHealthTracker` stores atomics for last success/start timestamps, current binary health status, waiting count, runtime state, failure/success streaks, offline timestamps, and last capacity probe.
- `DiskHealthTracker::mark_failure`, `mark_offline`, `mark_recovery_success`, `record_operation_success`, and `reset_for_store_init_retry` implement the runtime state machine.
- `LocalDiskWrapper` owns an `Arc<LocalDisk>`, a shared `DiskHealthTracker`, a `CancellationToken`, a cached disk id, and the timeout health policy.
- `LocalDiskWrapper::track_disk_health_with_op_and_timeout_action` is the core wrapper around local disk futures; it rejects faulty/stale disks, increments waiting counters, applies timeout, records success, and optionally marks timeout as a health failure.
- The `DiskAPI for LocalDiskWrapper` implementation delegates every disk operation to `LocalDisk` while applying operation-specific timeout and health policy.

## Control Flow
Wrapper construction combines the caller's `health_check` flag with `RUSTFS_DRIVE_ACTIVE_MONITORING`; it records the drive as online. `enable_health_check` spawns `monitor_disk_writable`, which periodically skips recently successful drives, writes and reads a test object under `.rustfs.sys/tmp`, deletes it, and marks failures. Once a drive becomes offline, `monitor_disk_status` probes at the configured returning interval until enough consecutive successes move the drive from `Offline` to `Returning` to `Online`.

Normal operations flow through `track_disk_health_with_op_and_timeout_action`: first fail fast on a faulty drive, then call `check_disk_stale`, update `last_started`, increment `waiting`, and execute either directly or under `tokio::time::timeout`. Successes update `last_success` or advance recovery. Timeouts decrement `waiting`, emit `rustfs_drive_op_timeout_total`, log structured warnings, and return `DiskError::Timeout`; depending on `TimeoutHealthAction`, the timeout may also advance the health state and spawn a recovery monitor.

The `DiskAPI` delegation is not uniform. Metadata, disk-info, list-dir, and walk-dir use dedicated timeout getters. `walk_dir` always ignores timeout failures for health marking because writer backpressure and scanner stalls should not poison a drive. `read_metadata`, `list_dir`, and `disk_info` use the scanner-sensitive timeout policy, so an env policy can also avoid marking scanner timeouts as disk failures. Many file/data operations use the max timeout, while append/create/list/delete/verify paths sometimes use `Duration::ZERO`, meaning no total timeout but still health and stale checks. `delete_versions` is custom because it returns per-item errors instead of one `Result`.

## State And Persistence Behavior
The persistent state guarded here is not written directly by this file, but it validates and caches the disk id read from `LocalDisk::get_disk_id`, and updates `GLOBAL_LOCAL_DISK_ID_MAP` for local disk ids. Health state is in-memory atomics and exported through metrics. Capacity probe state is also in-memory and records total/used/free plus timestamp. `reset_health_for_store_init_retry` exists because store initialization reuses disk handles across format-load retries; without clearing transient faulty marks, later retries would fail before issuing disk I/O.

The active health check writes temporary test objects and deletes them, so it has real filesystem side effects under the system bucket. The wrapper's `close` cancels monitoring before closing the underlying disk, but spawned monitors use shared cancellation and may otherwise continue until cancellation or recovery.

## Dependencies And Integration Points
The wrapper depends on `crate::disk::local::LocalDisk` for actual storage, `DiskAPI` for the trait boundary, `health_state.rs` for runtime-state classification and metrics helpers, `GLOBAL_LOCAL_DISK_ID_MAP` for local id lookup, `rustfs_config`/`rustfs_utils` for env configuration, `metrics` for counters, `tracing` for structured events, `uuid` for disk/test ids, and Tokio for async locking, timing, and task spawning.

This file is re-exported through `disk/mod.rs`, where `new_disk` constructs `Disk::Local(Box<LocalDiskWrapper>)`. `set_disk/lock.rs` uses runtime state and reset hooks during membership and init retry. `store/init.rs` calls disk health reset before retrying format load. `rpc/remote_disk.rs` and `rpc/peer_s3_client.rs` reuse `DiskHealthTracker` and timeout getters for remote health monitoring, keeping local and remote behavior aligned.

## Risks And Edge Cases
- The state machine relies on atomics but not a single synchronized transition lock; concurrent failures and successes may race, especially around consecutive counters and `offline_since`.
- `monitor_disk_writable` increments `waiting` before spawning a recovery monitor and comments that it balances a failed operation; mismatches could skew `total_waiting`.
- Health checks write into `.rustfs.sys/tmp`; delete failures are treated as operation failures unless `check_faulty_only` suppresses non-faulty errors, so system-bucket permission or cleanup issues can affect health signals.
- `Duration::ZERO` disables timeout entirely. That is intentional for streaming or immediate operations, but hung futures still hold waiting counts until they complete.
- Scanner/listing timeout policy is subtle. A default or env change can decide whether slow metadata/listing marks a drive unhealthy.
- The disk-id stale check allows a missing stored disk id during initialization; callers must ensure later formatted disks get validated.

## Test Signals
The in-file tests cover timeout env fallback and precedence, high-latency profile selection, invalid policy fallback, active-check interval/timeout env reads, online/suspect/offline/returning transitions, operation success recovery from suspect state, ignored timeout behavior, walk-dir writer backpressure, `skip_total_timeout`, follow-up operations after walk timeout, default timeout health marking, timeout health policy parsing, and store-init health reset. Integration tests in `set_disk.rs`, `set_disk/lock.rs`, `disk/mod.rs`, and `remote_disk.rs` exercise runtime health membership, reset delegation, and local/remote parity.
