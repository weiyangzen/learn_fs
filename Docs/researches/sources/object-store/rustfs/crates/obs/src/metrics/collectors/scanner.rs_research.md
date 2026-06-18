# sources/object-store/rustfs/crates/obs/src/metrics/collectors/scanner.rs

Purpose: converts background scanner telemetry into a large fixed metric set covering scan totals, active paths, concurrency queues, throttle/yield configuration, bitrot cycle settings, current-cycle progress, last-cycle summary, failures, and partial-cycle reasons.

Important APIs/types: `ScannerStats` contains numerous fields for cumulative scan counts, current queue/active counts, boolean config, current cycle, last cycle, and partial reason counters. `collect_scanner_metrics(&ScannerStats)` emits 68 metrics. `bool_metric_value` converts booleans to 1.0/0.0.

Control flow: fixed vector literal maps each stat field to a schema descriptor. Most metrics are unlabeled. `SCANNER_PARTIAL_CYCLES_BY_REASON_MD` is emitted four times with `reason` labels `unknown`, `runtime`, `objects`, and `directories`.

State/persistence: no local state. It reports scanner runtime state supplied by `stats_collector::collect_scanner_metric_stats`.

Dependencies/integration: used by the scheduler background workflow task, combined with optional ILM metrics. It depends heavily on `schema::scanner` descriptor coverage.

Risks: large fixed mapping is easy to desynchronize when `ScannerStats` or schema evolves. Numeric enums (`current_scan_mode`, `last_cycle_result`, `last_cycle_partial_reason`) need external documentation. A default struct emits 68 zero metrics, which may mask disabled/unavailable scanner collection if optional source checks are not preserved.

Test signals: unusually strong tests assert 68 metrics, many exact descriptor/value pairs, labeled partial reasons, and default zero behavior including reason label validation.
