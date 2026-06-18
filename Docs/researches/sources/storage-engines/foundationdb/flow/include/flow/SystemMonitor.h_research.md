<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SystemMonitor.h -->
# sources/storage-engines/foundationdb/flow/include/flow/SystemMonitor.h

Purpose: This header declares system and network monitoring state used by FoundationDB trace and metric emission. It collects machine identity, process/system statistics, network counters, and memory-limit monitoring hooks.

Important APIs and types: `SystemMonitorMachineState` stores optional folder, locality ids, IP, version, and monitor start time. Functions include `initializeSystemMonitorMachineState`, `machineStartTime`, `systemMonitor`, `customSystemMonitor`, `getSystemStatistics`, and `startMemoryUsageMonitor`. `NetworkData` holds many network, file-cache, task, TLS, and run-loop counters and has `init`. `StatisticsState` groups `SystemStatisticsState*`, `NetworkData`, and `NetworkMetrics`.

Control flow: Initialization stores machine context. `systemMonitor` and `customSystemMonitor` collect `Platform.h` statistics plus network counters and emit events/metrics in implementation. `startMemoryUsageMonitor` starts an actor that watches memory usage against a limit.

State and persistence behavior: Runtime state includes optional identity fields, monitor start time, cumulative/delta counters, and system statistics state for computing deltas. Persistence is through trace and metric outputs, not direct files in this header.

Dependencies and integration points: It depends on `Platform.h` for system stats and `TDMetric.h` for metric handles. It integrates with the Flow network, trace logging, machine locality, TLS policy failure counters, file cache metrics, and memory-limit enforcement.

Risks: Many counters have mixed semantics and can be platform-dependent. Optional machine identity must be initialized before monitor output is meaningful. Memory monitoring can terminate or alarm under configured limits, so false positives matter. Some fields are process-specific while others are machine-wide.

Test signals: Tests should validate initialization, `machineStartTime`, custom event emission, counter initialization, platform-specific stat collection, memory monitor behavior at thresholds, and stable field names in trace/metric output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SystemMonitor.h -->
