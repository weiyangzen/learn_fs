<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/process.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/sampler/process.rs

### Purpose
Samples current-process CPU, memory, uptime, disk I/O, file descriptors, task count, lock counts, and platform-specific process counters.

### Important APIs, Types, And Functions
`ProcessResourceSnapshot` contains CPU percent, memory bytes, and uptime. `ProcessStatusSnapshot` maps selected `sysinfo::ProcessStatus` variants to stable numeric categories. `ProcessSystemSnapshot` contains lock counts, CPU total seconds, task count, disk bytes, platform I/O counters, start/uptime, file descriptor limits/open counts, syscall totals, resident/virtual/peak memory, status, and status value. APIs are `snapshot_process_resource`, `snapshot_process_system`, and `snapshot_process_resource_and_system`.

### Control Flow
A static `OnceLock<Mutex<System>>` caches a sysinfo `System`. Snapshot refreshes the current PID with `ProcessRefreshKind::everything`, obtains platform stats and lock counts, then maps sysinfo process fields plus platform optional values into resource and system snapshots. If the process is missing, default snapshots are returned.

### State And Persistence
The cached `System` object persists for process lifetime and is protected by a mutex that tolerates poison by taking the inner value. Snapshots are immutable value copies.

### Dependencies And Integration Points
Depends on `sysinfo`, `process_lock_metrics`, and sampler system wrapper. Re-exported from sampler/mod and lib.rs. Intended for periodic resource telemetry collection.

### Risks
Sampling uses a global mutex, so high-frequency sampling can contend. Some fields are semantically inherited from Go-style metrics (`go_routine_total`) but actually map to sysinfo tasks, which can confuse dashboard naming. Platform stats default to zero when unavailable, so consumers need to distinguish unavailable from true zero through platform knowledge.

### Test Signals
Tests validate status mapping and that snapshots are collectable for the current process.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/process.rs -->
