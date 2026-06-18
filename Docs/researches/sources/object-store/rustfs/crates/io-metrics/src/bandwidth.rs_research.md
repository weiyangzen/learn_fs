<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/bandwidth.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/bandwidth.rs

### Purpose
Maintains a recent bandwidth estimate using an exponential moving average and classifies the estimate into low, medium, high, or unknown tiers.

### Important APIs, Types, And Functions
`BandwidthTier` is a local tier enum. `BandwidthSnapshot` returns current bytes/sec plus tier. `BandwidthMonitor` stores EMA beta, low/high thresholds, and optional current BPS. It exposes `new`, `record_transfer`, `current_bytes_per_second`, `snapshot`, and `tier_for`.

### Control Flow
`new` clamps `ema_beta` to `[0, 1]`. `record_transfer` ignores zero-byte or zero-duration samples, computes sample BPS, and either initializes or updates EMA as `beta * sample + (1 - beta) * current`. `snapshot` converts the optional estimate to zero if absent and classifies via `tier_for`.

### State And Persistence
State is a single in-memory `Option<f64>` inside the monitor. There is no synchronization or persistence.

### Dependencies And Integration Points
Uses only `Duration`. Complements top-level `record_bandwidth` metrics and `io-core` scheduler bandwidth tiering but defines its own `BandwidthTier` type rather than reusing `io-core`.

### Risks
Threshold ordering is not validated; if low threshold exceeds high threshold, tier classification can be surprising. With `ema_beta = 0`, the first sample sticks forever; with `ema_beta = 1`, only the latest sample matters. `snapshot` reports absent bandwidth as `0` and `Unknown`, so callers must distinguish unknown from measured zero only through tier.

### Test Signals
Unit test verifies EMA update from 1000 to 600 BPS with beta 0.5 and resulting medium tier.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/bandwidth.rs -->
