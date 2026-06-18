# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeInfoMetrics.java

Purpose: Per-HDDS-volume metrics source for capacity, availability, used space, reserved space, min-free thresholds, container count, scan counts, soft/hard min-free request counters, and RocksDB compaction latency.

Important APIs and types: Constructor registers a metrics source per identifier. Annotated getters expose storage type, storage directory, datanode UUID, layout version, volume state/type, committed bytes, and container count. Mutators update scan counters, min-free-space request counters, reserved-limit and insufficient-space gauges, and DB compaction rate.

Control flow: `getMetrics` snapshots the volume's `VolumeUsage`, computes real filesystem usage and Ozone-adjusted usage, then emits gauges for Ozone capacity/available/used, reserved, filesystem capacity/available/used, min-free space, and non-Ozone used.

State and persistence: Runtime metrics only. Values derive live from `HddsVolume` and `VolumeUsage`.

Dependencies and integration points: Created by `HddsVolume`; `HddsVolume.checkVolumeUsages` updates gauges; `HddsVolume.compactDb` records compaction latency. Used by reporting/monitoring systems through Metrics2.

Risks: The metrics source holds a strong reference to its volume until unregistered. `getMetrics` skips capacity gauges if `VolumeUsage` is null, which can happen for failed placeholders. Tests should cover gauge derivation with reserved space, scan skipped counters, soft/hard min-free counters, and unregister on failure/shutdown.
