<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/system.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/sampler/system.rs

### Purpose
Thin wrapper exposing platform-specific process counters through the sampler namespace.

### Important APIs, Types, And Functions
`snapshot_process_platform` returns `ProcessPlatformSnapshot` by calling `crate::snapshot_process_platform_stats()`.

### Control Flow
The function is a direct delegation.

### State And Persistence
No state.

### Dependencies And Integration Points
Depends on `ProcessPlatformSnapshot` and the crate-level re-export of process platform stats. Used by sampler re-exports and callers that want only platform-specific counters.

### Risks
All risks are inherited from `process_lock_metrics::snapshot_process_platform_stats`: OS-dependent availability, external command failures on some platforms, and default/optional values.

### Test Signals
No local tests; behavior is covered by process/platform tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/system.rs -->
