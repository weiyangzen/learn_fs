# sources/object-store/minio/cmd/metrics-v3-system-cpu.go

Purpose: Exposes v3 node CPU metrics for load, load percentage, user/system/nice/steal percentages, and average idle/iowait resource metrics.

Important APIs/types/functions: Defines CPU descriptor constants and `loadCPUMetrics`. The loader reads cached `madmin.CPUMetrics` and `resourceMetricsMap`.

Control flow: The loader retrieves `c.cpuMetrics`. If load stats exist, it sets 1-minute load and load percent rounded to two decimals. If time stats exist, it computes total CPU time and sets user/system/nice/steal percentages rounded to two decimals. It then looks up CPU idle and iowait averages in `resourceMetricsMap[cpuSubsystem]`.

State and persistence behavior: Stateless loader over one-minute cached CPU metrics and global resource metrics map. Values are current sampled percentages, not cumulative counters.

Dependencies and integration points: Depends on `metricsCache.cpuMetrics`, madmin CPU collection, `resourceMetricsMap`, `getResourceKey`, and CPU resource constants. It is part of system/node v3 metrics.

Risks: Division by zero is possible if `CPUCount` or total CPU time is zero, though upstream metrics likely populate them. Cache errors are ignored. Values are rounded, which is useful for display but loses precision.

Test signals: No direct tests in this subset.
