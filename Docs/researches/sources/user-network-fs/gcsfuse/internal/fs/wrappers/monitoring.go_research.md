<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring.go

Purpose: FUSE filesystem wrapper that records operation counts, error counts by low-cardinality category, latency, and read block sizes for metrics.

Important APIs/types/functions: constants for metrics error categories; helper `categorize`; `recordOp`; constructor `WithMonitoring`; type `monitoring`; `invokeWrapped`; delegators for all FUSE operations. `ReadFile` additionally calls `metricHandle.ReadBlockSizes`.

Control flow: each wrapper method calls `invokeWrapped` with a `metrics.FsOp` label. `invokeWrapped` records start time, invokes the wrapped method, and calls `recordOp`. `recordOp` increments operation count, increments error count when non-nil using `categorize`, and records latency.

State and persistence behavior: stateless wrapper except for metric side effects in the provided `metrics.MetricHandle`. It does not mutate filesystem data.

Dependencies and integration points: used by `fs.NewServer` as the outer wrapper. It relies on errno-like errors from inner wrappers for categorization and on generated metric attribute constants.

Risks: because monitoring is outside error mapping in `NewServer`, category labels are based on mapped errno. If wrapper order changes, non-errno errors default to IO error and category quality drops. The large errno switch must stay aligned with supported Linux errno constants and generated metric labels.

Test signals: companion test verifies representative errno-to-category mappings and fallback for non-errno errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring.go -->
