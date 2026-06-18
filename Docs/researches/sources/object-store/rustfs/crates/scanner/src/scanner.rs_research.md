# sources/object-store/rustfs/crates/scanner/src/scanner.rs

## Purpose

`scanner.rs` owns the scanner runtime loop. It configures deployment defaults, decides startup and inter-cycle delays, elects a single scanner through a namespace lock, runs namespace scans with budget cancellation, persists cycle/background-heal/data-usage state, and emits scanner metrics. It is the orchestration layer above cache definitions, folder scanning, scanner IO, runtime config, and sleeper behavior.

## Important APIs, Types, and Functions

- Runtime setup and loop:
  - `init_data_scanner(ctx, storeapi)` configures defaults, refreshes runtime config, and spawns the background scanner task.
  - `run_data_scanner(ctx, storeapi)` acquires the leader lock, restores cycle state, runs one immediate cycle, then repeats after randomized delays.
  - `run_data_scanner_cycle` performs one scan cycle and handles metrics, background heal mode, budget partials, and state persistence.
- Timing helpers:
  - `randomized_cycle_delay_for` applies +/-10% jitter with a one-second floor.
  - `initial_scanner_delay_for_startup` skips startup delay when there are buckets and either the usage cache is cold or active replication rules exist.
  - `read_data_usage_config_for_startup`, `persisted_usage_cache_is_cold_for_startup`, and `initial_scanner_startup_usage_state` inspect existing usage state before deciding startup delay.
- Default configuration:
  - `ScannerMaintenanceFeatures` records lifecycle/replication/inspection-failure signals.
  - `detect_scanner_maintenance_features` scans bucket lifecycle and replication configs.
  - `configure_scanner_defaults` applies single-disk defaults: slowest speed and a 24-hour cycle only when no maintenance feature requires regular scans.
- Background heal:
  - `BackgroundHealInfo` serializes bitrot scan start time/cycle and current scan mode.
  - `read_background_heal_info` and `save_background_heal_info` persist this JSON state.
  - `get_cycle_scan_mode`, `background_heal_info_for_scan_start`, `should_reset_bitrot_start`, and `background_heal_info_for_scan_complete` choose and record normal vs deep healing.
- Persistence:
  - `store_data_usage_in_backend` receives `DataUsageInfo` snapshots and writes `.usage.json` plus periodic `.bkp`.
  - Cycle state is read/written at `DATA_USAGE_BLOOM_NAME_PATH`; new format stores `next` as eight little-endian bytes followed by marshaled `CurrentCycle`.
- Observability:
  - Emits scan cycle complete/partial metrics, current scan mode, cycle config, and structured logs.
  - Uses `ScannerActivityGuard` around cycle work and backend usage saves.

## Control Flow

Startup calls `configure_scanner_defaults`, initializes the global sleeper, refreshes runtime config, then spawns a loop. Before the first cycle, the spawned task inspects buckets and persisted usage cache. If cache is cold with buckets, or active replication exists with buckets, it skips startup delay; otherwise it sleeps a randomized delay based on explicit start delay or scanner cycle interval.

`run_data_scanner` obtains a write namespace lock on `RUSTFS_META_BUCKET/leader.lock`. Lock creation or contention logs and returns `Ok(())`, so only the elected node proceeds. It restores `CurrentCycle` from `.bloomcycle.bin`, supporting both the old eight-byte `next` format and the newer `next + marshaled CurrentCycle` format. It runs one immediate cycle after lock acquisition, then loops with cancellation-aware randomized sleep.

`run_data_scanner_cycle` refreshes runtime config, records configured cycle/bitrot/budget metrics, publishes current cycle state, reads background heal info, chooses scan mode, and starts a `store_data_usage_in_backend` task receiving `DataUsageInfo` updates from `nsscanner`. It constructs a `ScannerCycleBudget` child token and passes it to `storeapi.nsscanner`. If `nsscanner` returns because a budget elapsed, the cycle is marked partial, source/reason metrics are emitted, current scan mode is cleared, and `cycle_info.current` is reset to idle without advancing `next`. Other scan errors emit failed completion metrics. Successful cycles emit success metrics, complete deep-scan background-heal state if needed, advance `cycle_info.next`, append completion time, trim recent completions, publish metrics, and persist cycle state.

`store_data_usage_in_backend` drains usage snapshots from a channel until closed or canceled. For each snapshot it reads the existing persisted `.usage.json`; if both timestamps exist and the incoming snapshot is not newer, it skips saving to avoid overwriting fresher state. Every eleventh attempt writes a backup first, then writes the main JSON and refreshes in-memory bucket usage on success.

## State and Persistence Behavior

Process-local state includes runtime config, scanner activity, current metrics, and background task lifetimes. Persisted scanner state includes:

- `.usage.json`: JSON `DataUsageInfo`, updated from scanner output.
- `.usage.json.bkp`: periodic backup written by `store_data_usage_in_backend`.
- `.bloomcycle.bin`: cycle number and marshaled `CurrentCycle`.
- `.background-heal.json`: JSON `BackgroundHealInfo`, skipped entirely for ErasureSD setups.

Partial budget cycles do not advance `cycle_info.next`; they publish idle current-cycle state and rely on lower-level partial cache/checkpoint behavior to resume usage work. Completed cycles retain only a bounded list of recent completion timestamps using `data_usage_update_dir_cycles()`.

## Dependencies and Integration Points

- Depends on `runtime_config.rs` for start delay, cycle interval, bitrot cycle, budget config, and runtime refresh.
- Depends on `scanner_budget.rs` to bound cycles by duration/object/directory budgets.
- Depends on `scanner_io::ScannerIO` for `storeapi.nsscanner`.
- Depends on `scanner_folder` for update-cycle retention and heal selection probability.
- Uses `rustfs_ecstore` for bucket listing, metadata locks, lifecycle/replication configs, config persistence, and `ECStore`.
- Uses `rustfs_common::metrics` for cycle metrics and scan modes.
- Uses `tokio` tasks/channels/timers and `CancellationToken`.
- Lifecycle integration tests call `init_data_scanner`, and unit tests in this file exercise timing, budget mapping, stale snapshot protection, and background-heal state transitions.

## Risks and Edge Cases

- Lock contention and lock creation errors return `Ok(())`, so external callers may see no error even when this node did not scan.
- Startup delay skips for active replication to recover failed-status objects quickly; incorrect replication feature detection can affect scan latency.
- Cycle state decode failure logs and continues with the parsed `next` prefix or default state, which may lose recent completion history.
- `store_data_usage_in_backend` protects only timestamped snapshots. If timestamps are missing, stale overwrite protection does not apply.
- Backup writes in `store_data_usage_in_backend` are based on attempt count, not elapsed time or data size.
- A budget-elapsed partial cycle returns without awaiting the backend saver task explicitly; channel closure and task completion depend on sender/drop behavior in the scan path.
- Single-disk default cycle behavior depends on lifecycle/replication inspection. Inspection failure preserves regular speed-based cycles to avoid missing maintenance work.

## Test Signals

Tests cover randomized delay bounds, startup delay skip/keep cases, cycle budget env configuration, zero budget disabling, budget cancellation/drop behavior, partial reason/source metric mapping, idle marking after partial cycles, stale snapshot preservation, cycle interval precedence, MinIO env aliases, single-disk default cycle decisions, bitrot/deep-scan mode selection, background-heal start/complete transitions, and recent completion retention. These tests signal that operational timing, partial-cycle semantics, and persistence ordering are the highest-risk contracts.
