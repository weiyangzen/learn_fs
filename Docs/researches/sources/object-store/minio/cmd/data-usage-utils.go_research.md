<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-utils.go -->
## sources/object-store/minio/cmd/data-usage-utils.go

Purpose: This file defines the public data usage structures and conversion helpers used to expose MinIO cluster, bucket, replication, and tier usage statistics. It is the JSON/API-facing model for scanner output.

Important APIs and types: `BucketTargetUsageInfo` reports per-replication-target bytes and counts for pending, failed, replicated, and replica objects. `BucketUsageInfo` reports bucket size, object/version/delete-marker counts, object-size and version histograms, replica counters, and per-target replication details; fields suffixed `V1` exist for backward compatibility with older replication accounting. `DataUsageInfo` aggregates cluster capacity, object/version/delete-marker totals, bucket count, per-bucket usage, legacy `BucketSizes`, optional replication info, and optional `TierStats`. Methods `DataUsageInfo.tierStats()` and `DataUsageInfo.tierMetrics()` transform internal tier statistics into admin API and metrics forms.

Control flow: `tierStats()` returns nil when no tier stats exist or tier configuration is empty. Otherwise it asks `allTierStats.populateStats` to fill `madmin.TierStats`, wraps each tier as `madmin.TierInfo`, adds tier type from `globalTierConfigMgr`, and sorts internal tiers first, then remaining tiers by name. `tierMetrics()` returns one metric each for transitioned bytes, transitioned objects, and transitioned versions per tier, using metric descriptors from cluster ILM metric helpers and labeling each sample by tier.

State and persistence behavior: The structs are serialized to JSON for `.usage.json` and API responses. `DataUsageInfo.TierStats` points to scanner/cache tier state persisted in the data usage cache. Compatibility is explicit: both new `BucketsUsage` and deprecated `BucketSizes` are retained, and V1 replication fields are still present so older persisted JSON can be upgraded by `loadDataUsageFromBackend`.

Dependencies and integration points: The file depends on `sort`, `time`, and `github.com/minio/madmin-go/v3`. It integrates with scanner cache aggregation, admin APIs, Prometheus metrics (`MetricV2`), global tier configuration, and replication config migration in `data-usage.go`.

Risks: These structs are API contracts; JSON tag changes or field removals can break clients. `tierStats()` depends on global tier config state, so tier stats can disappear from output when configuration is empty even if cache data exists. Sorting gives internal tiers priority with a comparator that returns true whenever the left item is internal, so multiple internal tiers rely on sort behavior rather than secondary ordering.

Test signals: There are no direct tests in this file. Coverage is indirect through data usage serialization tests, scanner tests, and any API/metrics tests that consume `DataUsageInfo`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-utils.go -->
