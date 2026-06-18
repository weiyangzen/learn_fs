# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeHealthMetrics.java

Purpose: Metrics source tracking total, healthy, and failed volume counts per volume type on a datanode.

Important APIs and types: Static `create(StorageVolume.VolumeType)` registers a metrics source named with the volume type. Methods increment/decrement healthy and failed counters, `unregister` removes the source, and `getMetrics` emits gauges.

Control flow: `MutableVolumeSet` creates one instance per set, increments healthy/failed counts during initialization, adjusts counts during failure transitions, and unregisters on shutdown.

State and persistence: Runtime metrics state only, stored in `AtomicInteger` counters. No durable state.

Dependencies and integration points: Uses Hadoop Metrics2 `DefaultMetricsSystem`, `MetricsRegistry`, `Interns`, and `MetricsSource`.

Risks: Counter decrement methods do not guard against negative values, so callers must maintain balanced transitions. Tests should cover registration naming, gauge values after transitions, unregister behavior, and failure during volume-set initialization.
