# sources/sync-backup/syncthing/lib/scanner/metrics.go

## Purpose
Defines Prometheus metrics for scanner activity and ensures per-folder series are registered before nonzero activity.

## Important APIs, Types, and Functions
`metricHashedBytes` is a counter vector `syncthing_scanner_hashed_bytes_total` labeled by folder. `metricScannedItems` is a counter vector `syncthing_scanner_scanned_items_total` labeled by folder. `registerFolderMetrics` initializes label values for a folder.

## Control Flow
Metric vectors are created at package initialization through `promauto`. `registerFolderMetrics` calls `WithLabelValues` for both metrics to create zero-valued time series.

## State and Persistence Behavior
Metrics live in the process Prometheus registry. They are not persisted by this file. `HashFile` increments hashed bytes and `walkAndHashFiles` increments scanned items.

## Dependencies and Integration Points
Depends on `prometheus` and `promauto`. Called by `newWalker` for each scanned folder and by scanner code during walking/hashing.

## Risks and Edge Cases
Unbounded folder IDs could create high-cardinality metrics. Metric names and labels are part of monitoring contracts and should not change casually.

## Test Signals
No direct tests in this subset. Metrics can be validated by scanner tests that instantiate walkers and inspect registered counters, or by integration monitoring checks.
