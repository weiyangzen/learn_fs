# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/metrics.rs

Purpose: Metrics collection wrapper for proxy validation, cache behavior, and validation modes.

Important APIs: `ProxyMetrics::new`, `increment_validation_attempts`, `record_validation_success`, `record_validation_failure`, `record_validation_mode`, `record_cache_hit`, `record_cache_miss`, `set_cache_size`, `record_cache_metrics`, `print_summary`, and `default_proxy_metrics`.

Control flow: Constructor stores enabled flag/app label and registers metric descriptions if enabled. Every recorder returns immediately when disabled. Success/failure recorders emit counters, gauges, and histograms with `app` and error/mode labels. Failure type is derived by matching `ProxyError` variants.

State and dependencies: Lightweight cloneable struct with no metric state of its own; uses the global `metrics` facade and tracing.

Integration points: Optional in `ProxyValidator`, `IpValidationCache`, and global initialization. `default_proxy_metrics` uses app name `trusted-proxy`.

Risks and tests: Metric descriptions include `rustfs_trusted_proxy_validation_mode` gauge only indirectly through recorder, but no description is registered for that name. `record_cache_metrics` increments counters by supplied values, so callers must pass deltas rather than totals. Requested tests do not assert metrics.
