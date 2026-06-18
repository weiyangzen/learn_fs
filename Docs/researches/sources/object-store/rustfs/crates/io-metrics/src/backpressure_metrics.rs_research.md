<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/backpressure_metrics.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/backpressure_metrics.rs

### Purpose
Small metrics helper module for backpressure state transitions, request rejections, concurrent operation gauges, and activation/deactivation events.

### Important APIs, Types, And Functions
Exports `record_backpressure_state_change`, `record_backpressure_rejection`, `record_concurrent_operations`, `record_backpressure_activation`, and `record_backpressure_deactivation`.

### Control Flow
Each function is a direct `metrics` macro call. State changes increment a counter labeled by `from` and `to`. Rejections, activations, and deactivations increment counters. Concurrent operation count sets a gauge.

### State And Persistence
The module stores no local state. Persistence and aggregation are delegated to the installed metrics recorder/exporter.

### Dependencies And Integration Points
Integrates with any component enforcing queue or resource backpressure. Re-exported from `lib.rs`.

### Risks
Dynamic `from`/`to` strings can create high-cardinality metrics if callers do not use a constrained state vocabulary. There is no paired state machine here; caller correctness determines whether activation/deactivation counters balance.

### Test Signals
Unit tests execute each recorder to confirm compile-time and runtime macro paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/backpressure_metrics.rs -->
