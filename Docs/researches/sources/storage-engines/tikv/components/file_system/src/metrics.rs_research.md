<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics.rs -->
# sources/storage-engines/tikv/components/file_system/src/metrics.rs

Purpose: this module defines Prometheus metrics and TLS buffering for file-system I/O bytes, latency, and rate-limiter waits.

Important APIs and metrics: static metric label enums cover `IoType`, `IoOp`, and `IoPriority`. Registered metrics include `tikv_io_bytes` (`IntCounterVec` by type/op), `tikv_io_latency_micros` (`Histogram` by type/op), `tikv_rate_limiter_request_wait_duration_seconds` (`HistogramVec` by priority), and `tikv_rate_limiter_max_bytes_per_sec` (`IntGauge` by priority). `FileSystemLocalMetrics` buffers rate-limiter wait histograms in TLS. Public functions are `tls_flush` and `tls_collect_rate_limiter_request_wait`.

Control flow and state: metrics are globally registered through `lazy_static!`. Request wait observations are recorded into a thread-local local histogram and flushed by `tls_flush`, which `MetricsManager::flush` calls before byte collection.

Dependencies and integration points: `rate_limiter.rs` calls `tls_collect_rate_limiter_request_wait` after sleeping. `metrics_manager.rs` uses `IO_BYTES_VEC` and `tls_flush`. `biosnoop.rs` uses `IO_LATENCY_MICROS_VEC` when draining BPF histograms.

Risks: metric label enums must stay aligned with `IoType` names and eBPF histograms. The label enum currently omits `log_rewrite` despite `IoType::RewriteLog` existing in `lib.rs`, which can limit metric coverage if that type is used in generic iteration elsewhere. Registration unwraps can panic on duplicate metric names.

Test signals: no direct tests exist. Metrics are exercised indirectly by rate limiter and metrics manager tests/usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/file_system/src/metrics.rs -->
