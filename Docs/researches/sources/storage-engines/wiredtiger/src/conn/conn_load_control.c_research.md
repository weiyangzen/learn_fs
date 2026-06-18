# sources/storage-engines/wiredtiger/src/conn/conn_load_control.c

## Purpose
This file implements connection-level load-control configuration and load percentage calculation. Load control maps cache pressure to read and write load values so upper layers can reject work once configured thresholds are exceeded.

## Important APIs, Types, and Functions
The public functions are `__wti_conn_load_control_config`, `__wt_conn_calc_read_load`, and `__wt_conn_calc_write_load`. Local helpers are `__conn_load_control_configure` and `__conn_calc_load_pct`. Important state lives in `WT_CONNECTION_LOAD_CONTROL` and eviction/cache fields such as `conn->cache_size`, `evict->eviction_trigger`, and `evict->eviction_dirty_trigger`.

## Control Flow and Behavior
Configuration reads `load_control.enable` and sets `WT_CONN_LOAD_CONTROL` when enabled. It reads `load_control.control_threshold`, clamps the stored threshold to 200, and recalculates read/write maximum byte thresholds. Read load maps current cache bytes in use to the configured eviction trigger threshold. Write load maps dirty cache bytes to the eviction dirty trigger threshold. Both calculations saturate at 200% and update connection statistics.

## State and Persistence
State is volatile connection configuration: `read_load_max`, `write_load_max`, `control_threshold`, `read_load`, `write_load`, and the load-control enabled flag. There is no on-disk persistence. Reconfiguration recalculates thresholds because they depend on both load-control and eviction/cache settings.

## Dependencies and Integration Points
The file depends on configuration parsing, atomic stores, cache byte counters, eviction configuration, and connection stats. It is initialized in `__wti_connection_open` after cache/eviction setup and reconfigured from `__wti_conn_reconfig` after cache and eviction reconfiguration.

## Risks
Risks include stale thresholds if eviction or cache size changes without reconfiguration, integer truncation from double-based percentage thresholds, disabled load-control leaving old load values visible in stats, and threshold semantics changing if eviction trigger defaults change.

## Test Signals
Relevant signals are configuration tests for enable/disable and threshold clamping, stats for `read_load`/`write_load`, and workloads that drive clean or dirty cache pressure past the configured activation threshold.
