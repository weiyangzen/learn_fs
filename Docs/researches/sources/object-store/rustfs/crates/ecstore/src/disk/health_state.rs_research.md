# sources/object-store/rustfs/crates/ecstore/src/disk/health_state.rs

## Purpose
`health_state.rs` defines runtime drive health states, recovery classes, health threshold getters, metric-recording helpers, and membership snapshots for choosing disks based on health. It is the policy vocabulary used by local and remote disk health trackers, scanner/healing membership, and admin/metrics views.

## Important APIs, Types, And Functions
- `RuntimeDriveHealthState` is a `repr(u32)` enum with `Online`, `Suspect`, `Offline`, and `Returning`.
- `as_str`, `from_u32`, `is_snapshot_eligible`, `is_strictly_online`, and `should_probe_for_admin` expose state labels and policy checks.
- `DriveRecoveryClass` classifies recovery durations as `ShortOffline`, `MediumOffline`, or `LongOffline`.
- `get_drive_suspect_failure_threshold`, `get_drive_returning_success_threshold`, `get_drive_returning_probe_interval`, `get_drive_offline_grace_period`, and `get_drive_long_offline_threshold` read env-backed thresholds from `rustfs_config`.
- `classify_drive_recovery` maps offline duration to a recovery class using grace-period and long-offline thresholds.
- `record_drive_runtime_state`, `record_drive_state_transition`, `record_drive_recovery_class`, and `record_drive_offline_duration` emit metrics.
- `DriveMembershipSnapshot` groups `DiskStore` handles by runtime state and exposes scanner and strict-online candidate lists.

## Control Flow
State conversion is tolerant: unknown numeric values map to `Online`. Runtime metrics are recorded as one gauge per possible state, setting the current state to `1.0` and all others to `0.0` for a given endpoint/pool/set/disk label set. Transitions and recovery classes are counters, while offline duration is a gauge.

Recovery classification is threshold-based: durations up to the offline grace period are short, durations greater than or equal to the long-offline threshold are long, and everything between is medium. Membership snapshots iterate optional disks, skip `None`, query each disk's runtime state, and clone the `DiskStore` into the corresponding vector. Scanner/heal candidates include online, suspect, and returning disks. Strict online candidates include only online disks, with a local-only variant for local-disk operations.

## State And Persistence Behavior
This file does not persist data. It records metrics and constructs in-memory snapshots. Its threshold getters read environment variables each call, so tests and runtime changes can influence policy unless higher layers cache values. Runtime state itself is stored in `DiskHealthTracker` in `disk_store.rs` and remote disk equivalents; this module defines interpretation and metric emission.

## Dependencies And Integration Points
`disk_store.rs`, `rpc/remote_disk.rs`, and `rpc/peer_s3_client.rs` use the state enum, thresholds, recovery classification, and metric recorders while marking failures and recoveries. `disk/mod.rs` exposes `runtime_state` through the `Disk` abstraction. `set_disk/lock.rs` uses `DriveMembershipSnapshot` to choose scanner/heal candidates and strict online disks, and to reset offline disks before store-init retries. `set_disk.rs` and tests use state values for info reporting and behavior checks.

The module depends on `DiskAPI`/`DiskStore` for membership filtering, `Endpoint` for metric labels, `metrics` for counters/gauges, `rustfs_config`, and `rustfs_utils`.

## Risks And Edge Cases
- `from_u32` maps unknown values to `Online`, which is fail-open. That is convenient for default atomics but risky if memory corruption or incompatible states appear.
- Environment threshold getters cast `u64` to `u32` for counts. Very large env values can truncate.
- Metric labels include endpoint strings, which may have high cardinality in dynamic environments.
- Snapshot methods clone `DiskStore` handles; they are cheap if handles are Arcs/boxed wrappers, but candidate lists may become stale immediately after construction as health changes.
- `should_probe_for_admin` differs from scanner eligibility: suspect is snapshot eligible but not admin-probe eligible.

## Test Signals
The in-file test verifies snapshot eligibility policy: online, suspect, and returning are eligible, while offline is not. Broader behavior is covered by `disk_store.rs` tests for transitions, recovery thresholds, offline duration, and reset behavior, plus `set_disk/lock.rs` tests for membership candidate selection.
