# sources/object-store/minio/cmd/metrics-v3-system-memory.go

Purpose: Exposes v3 node memory metrics.

Important APIs/types/functions: Defines descriptors for total, used, free, buffers, cache, used percentage, shared, and available memory. `loadMemoryMetrics` populates values from cached `madmin.MemInfo`.

Control flow: The loader retrieves `c.memoryMetrics`, logs and returns the error if cache retrieval fails, then sets all memory gauges. Used percentage is calculated as `Used * 100 / Total`.

State and persistence behavior: Stateless over one-minute cached memory metrics. Values reflect madmin local host memory collection.

Dependencies and integration points: Depends on `metricsCache.memoryMetrics`, madmin memory collection, and v3 metrics framework.

Risks: Division by zero is possible if `Total` is zero. Unlike many other loaders, this one returns the cache error after logging, which can affect the metric group's collect error path. Metric units are bytes for most values but percentage for `used_perc`.

Test signals: No direct tests in this subset.
