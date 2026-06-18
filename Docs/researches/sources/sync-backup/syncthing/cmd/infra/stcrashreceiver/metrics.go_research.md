# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/metrics.go

Purpose: Prometheus metric definitions for the crash receiver service.

Important APIs/types/functions: promauto counters/gauges include `crash_reports_total{result}`, `failure_reports_total{result}`, `diskstore_files_total`, `diskstore_bytes_total`, `diskstore_oldest_age_seconds`, `sentry_reports_total{result}`, `ignore_matches_total{pattern}`, `source_code_loads_total{result}`, and `source_code_cache_size`.

Control flow: metrics are registered at package initialization. Other files increment or set them during HTTP handling, disk inventory/cleanup, Sentry send/parse, ignore matching, and source-code loading/cache hits.

State and persistence behavior: metrics are in-memory process state exposed through `/metrics` when metrics listening is enabled. Counters reset on process restart.

Dependencies/integration: uses Prometheus client_golang and `promauto`, and is served from `main.go` via `promhttp.Handler`.

Risks/test signals: high-cardinality `ignore_matches_total` can grow with many regex patterns, but patterns are admin-supplied. Signal is expected metric names and labels appearing in Prometheus scrape output after corresponding operations.
