# sources/sync-backup/syncthing/lib/model/metrics.go

Purpose: this file declares Prometheus metrics for the model package's folder state, folder summary counts, pull and scan activity, processed bytes, and conflict counts. It also provides `registerFolderMetrics` to pre-create labeled time series for a folder.

Important metrics: `metricFolderState` is a gauge labeled by folder. `metricFolderSummary` is a gauge labeled by folder, scope, and type; the promlinter warning is suppressed because one vector intentionally carries several summary dimensions. Pull and scan counters track total iterations and total seconds per folder. `metricFolderProcessedBytesTotal` tracks bytes by folder and source, with sources `network`, `local_origin`, `local_other`, and `skipped`. `metricFolderConflictsTotal` counts conflicts per folder.

Control flow: package initialization registers metrics through `promauto`, so importing the model package registers collectors globally. `registerFolderMetrics(folderID string)` touches each relevant label combination so counters and gauges exist even before nonzero activity. It initializes state, pulls, pull seconds, scans, scan seconds, processed byte sources, and conflicts. Folder summary scope/type combinations are updated in `folder_summary.go` when a summary is sent rather than pre-created here.

State and persistence behavior: metric state lives in Prometheus collector objects in process memory. It is not persisted by this file. Values are mutated by other model code during state transitions, scans, pulls, summaries, and conflict handling.

Dependencies and integration points: depends on `github.com/prometheus/client_golang/prometheus` and `promauto`. `folderstate.go` writes `metricFolderState`, `folder_summary.go` writes `metricFolderSummary`, and send/receive or scan paths update the counters. External integration is through Prometheus scraping and any API exposing registered metrics.

Risks: global `promauto` registration can panic on duplicate metric names if package-level registration is repeated in unusual test setups. Label cardinality is bounded by folder IDs and a small fixed set of scopes/types/sources, but folder churn can still grow metric series over process lifetime. Because folder summary uses a multi-dimensional generic gauge, consumers must interpret labels correctly.

Test signals: no direct tests in this subset. Runtime validation comes from metric scrape output and tests around state transitions, pulls, scans, and summaries that update the metrics.
