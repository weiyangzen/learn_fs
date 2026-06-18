<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/process_lock_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/process_lock_metrics.rs

### Purpose
Tracks process-held read/write lock counts and collects platform-specific process I/O and virtual memory counters.

### Important APIs, Types, And Functions
Static atomics `READ_LOCKS_HELD` and `WRITE_LOCKS_HELD` back lock count recorders. `ProcessLockSnapshot` reports current held locks. `ProcessPlatformSnapshot` reports optional I/O character/read/write bytes, syscall read/write totals, and peak virtual memory. Public APIs include acquire/release recorders, `snapshot_process_lock_counts`, and `snapshot_process_platform_stats`. Platform modules implement `snapshot` for Linux (`/proc/self/io` and `/proc/self/status`), Windows (PowerShell CIM), macOS/BSD (`ps`), and fallback unsupported targets.

### Control Flow
Acquire increments atomics. Release uses `fetch_update` with saturating subtraction to avoid underflow. Platform snapshot reads OS data and parses known fields into optional counters. Linux parsing extracts `rchar`, `wchar`, `syscr`, `syscw`, `read_bytes`, `write_bytes`, and `VmPeak`.

### State And Persistence
Held-lock counters are process-wide atomics and persist for the process lifetime or until test reset. Platform snapshots are instantaneous reads; nothing is persisted.

### Dependencies And Integration Points
Feeds `sampler/process.rs`, which combines lock counts with sysinfo process metrics. Re-exported from `lib.rs`.

### Risks
Lock counters depend on balanced acquire/release instrumentation by callers. Release saturation hides double-release bugs in metrics. Non-Linux platforms rely on external commands and may return default/partial snapshots. Parser functions ignore malformed lines and missing fields, which is resilient but can mask platform drift.

### Test Signals
Tests cover held-lock acquire/release saturation and parser helpers. Platform-specific Linux/macOS parser tests validate expected extraction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/process_lock_metrics.rs -->
