# sources/object-store/rustfs/crates/obs/src/metrics/schema/ilm.rs

## Purpose
Defines lifecycle management metric descriptors for expiry and transition queues, backpressure, compensation, and versions scanned.

## Important APIs, Types, and Functions
Exports nine `LazyLock<MetricDescriptor>` values. Queue depth and active/running values are gauges; missed, full, send-timeout, compensation scheduled, and versions scanned values are counters. All use `subsystems::ILM` and no labels.

## Control Flow
Only lazy descriptor initialization. Descriptor type choices are encoded in factory calls.

## State and Persistence
No values are stored. Runtime data comes from `collect_ilm_metric_stats()`, which reads `GLOBAL_ExpiryState`, `GLOBAL_TransitionState`, and `global_metrics().report()`.

## Dependencies and Integration Points
Used by `metrics/collectors/ilm.rs` to expose `IlmStats`. It integrates with lifecycle runtime state in `rustfs_ecstore` through the stats collector.

## Risks
Because all descriptors are unlabeled, bucket-specific or rule-specific ILM visibility is not represented here. Counter/gauge semantics need to stay aligned with collector values, especially compensation running versus compensation scheduled.

## Test Signals
No direct tests. Existing collector tests or snapshot checks should validate full names and types.
