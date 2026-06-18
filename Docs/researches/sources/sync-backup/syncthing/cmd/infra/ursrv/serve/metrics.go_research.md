# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/metrics.go

Purpose: defines operational Prometheus metrics for the usage reporting server itself.

Important APIs/state: counters and gauges include `metricReportsTotal`, `metricsCollectsTotal`, `metricsCollectSecondsTotal`, `metricsCollectSecondsLast`, `metricsRecalcsTotal`, `metricsRecalcSecondsTotal`, `metricsRecalcSecondsLast`, and `metricsWriteSecondsLast`.

Control flow: package initialization creates collectors with namespace `syncthing` and subsystem `ursrv_v2`. `init` prewarms `incoming_reports_total` labels `fail`, `replace`, and `accept`.

State and persistence: metrics are process-local. They summarize incoming report outcomes, custom collector recalculation/collection timing, and dump-file write timing.

Dependencies/integration: used by `serve.go` request handling and dump writes, and by `prometheus.go` custom collector recalculation/collection paths.

Risks and test signals: prewarming avoids missing series for dashboards. No direct unit tests are present for collector registration or label use.
