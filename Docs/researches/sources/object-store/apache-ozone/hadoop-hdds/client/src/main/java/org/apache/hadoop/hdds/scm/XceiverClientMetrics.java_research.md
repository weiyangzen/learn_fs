# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientMetrics.java

Purpose: Metrics source for storage container client operations and EC reconstruction counters.

Important APIs/types/functions: Tracks global `pendingOps`, `totalOps`, `ecReconstructionTotal`, and `ecReconstructionFailsTotal`, plus per-`ContainerProtos.Type` pending/op counters and latency `PerformanceMetrics`. `create` registers with `DefaultMetricsSystem`. `incrPendingContainerOpsMetrics`, `decrPendingContainerOpsMetrics`, and `addContainerOpsLatency` are called around requests. `getMetrics` snapshots all counters and latencies.

Control flow: `init` reads percentile intervals from an `OzoneConfiguration`, creates a registry, and initializes maps for every container command type. Request paths increment pending/total before async send, decrement and record latency on completion. `unRegister` closes latency metrics and unregisters the source.

State and persistence behavior: Holds mutable counters, maps, and registry in process memory. Export is through Hadoop metrics.

Dependencies and integration points: Created by `XceiverClientManager` and used by gRPC, Ratis, and datastream write paths. Depends on Hadoop metrics2 and Ozone `PerformanceMetrics`.

Risks: `reset()` calls `init()` without unregistering previous registry-derived metrics, so tests must isolate carefully. `decrPendingContainerOpsMetrics` uses `incr(-1)`, relying on Hadoop metrics allowing negative increments. Creating a new `OzoneConfiguration` inside metrics ignores caller-specific percentile config unless globally loaded.

Test signals: Tests should validate per-command counters, pending decrement, latency snapshot presence, EC reconstruction counters, reset behavior, and unregister cleanup.
