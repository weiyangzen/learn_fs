# sources/object-store/rustfs/crates/obs/src/metrics/schema/scanner.rs

## Purpose
Defines the scanner metric surface for lifetime counters, current activity, concurrency, throttling configuration, current cycle stats, last cycle stats, failure/partial counters, and partial-cycle reasons.

## Important APIs, Types, and Functions
Exports many `LazyLock<MetricDescriptor>` values under `subsystems::SCANNER`. Lifetime scan counts and failed/partial cycles are counters. Activity gauges cover last activity, active paths, concurrency, throttle settings, cycle budgets, current/last cycle counters encoded as gauges, scan modes, result codes, rates, and durations. `SCANNER_PARTIAL_CYCLES_BY_REASON_MD` has a `reason` label.

## Control Flow
The file is static schema only. Descriptor types and help text encode the metric contract. Runtime mapping occurs in `collect_scanner_metric_stats()` and `metrics/collectors/scanner.rs`.

## State and Persistence
No local state or persistence. Runtime scanner values come from `rustfs_common::metrics::global_metrics().report()` and are transformed in `stats_collector.rs`.

## Dependencies and Integration Points
Used heavily by `metrics/collectors/scanner.rs`, which imports nearly every descriptor and emits values from `ScannerStats`. The schema integrates with `HealScanMode` through numeric mode code descriptions in help text, but the conversion code lives in `stats_collector.rs`.

## Risks
The surface is broad, so collector/schema drift is likely when adding scanner fields. Many current-cycle counts are gauges because they describe an in-progress cycle rather than process lifetime counters. Numeric enum encodings for modes/results/partial reasons need external documentation or dashboard annotations. Only the reason-specific partial-cycle metric uses a label.

## Test Signals
No direct schema tests. `stats_collector.rs` has tests for scanner cycle age, scan-mode mapping, fallback started counts, and rate calculations. Collector tests should verify all descriptors are emitted with correct names and reason labels.
