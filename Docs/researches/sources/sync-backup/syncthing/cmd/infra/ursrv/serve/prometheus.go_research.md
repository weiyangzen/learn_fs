# sources/sync-backup/syncthing/cmd/infra/ursrv/serve/prometheus.go

Purpose: builds a dynamic Prometheus collector from `contract.Report` struct tags, aggregating usage report data into gauges, gauge vectors, and custom summaries.

Important APIs/types/functions: `metricsSet`, `newMetricsSet`, `fieldNameTypeLabel`, `nameConstLabels`, `Serve`, `recalc`, `addReport`, `addReportStruct`, `Describe`, `Collect`, and `metricSummary` with `Observe`, `Collect`, and `Reset`.

Control flow: `newMetricsSet` reflects over `contract.Report` fields recursively and creates collectors based on `metric` tags. `Serve` triggers recalculation on a five-minute boundary. `recalc` resets collectors, deletes stale reports older than the negative cutoff, and re-adds all remaining reports. `Collect` exposes the current calculated values under a read lock while updating collection timing metrics.

State and persistence: state is in memory in maps of Prometheus collectors and summary accumulators. Source data lives in `server.reports`; stale report pruning mutates that map. Custom summaries retain value slices until each recalculation resets them.

Dependencies/integration: depends heavily on `lib/ur/contract` metric tags, Prometheus collector interfaces, `xsync` report storage via `server`, reflection, sorting, and `serve.go` report enrichment.

Risks and test signals: reflection tag mistakes can silently create empty metric names or missing labels. In the `map[string]int` gaugeVec branch, `field.SetInt` is attempted on a map-valued reflect field, which looks suspicious and could panic if hit. `metricSummary.Collect` returns from the whole method when it sees an empty value slice, potentially skipping later labels. No direct tests cover these collector edge cases.
