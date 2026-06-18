# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MutableVolumeSet.java

Purpose: Owns a datanode's active and failed volumes for one `StorageVolume.VolumeType`. It initializes configured locations, runs health checks, moves failed volumes out of service, reports volume state, and exposes lifecycle operations.

Important APIs and types: Implements `VolumeSet`. Key methods include `checkAllVolumes`, `checkVolumeAsync`, `failVolume`, `startAllVolume`, `refreshAllVolumeUsage`, `setGatherContainerUsages`, `hasEnoughVolumes`, `getStorageReport`, and lock methods. It maintains `volumeMap`, `failedVolumeMap`, `ReentrantReadWriteLock`, `StorageVolumeChecker`, selected `StorageVolumeFactory`, and `VolumeHealthMetrics`.

Control flow: Construction registers with a checker, selects a volume factory and tolerated-failure count based on volume type, creates metrics, then initializes configured directories. Initialization parses storage locations, creates volumes, ensures directories and data permissions, records successes, and converts failures to failed-volume placeholders. Health checks snapshot active volumes, ask `StorageVolumeChecker`, and call `handleVolumeFailures` for failed results. Failure handling acquires the write lock, marks volumes failed, updates maps and metrics, checks fatal tolerance, and runs an optional listener.

State and persistence: Active and failed volume maps are runtime state. Persistent effects are delegated to volume constructors and directory permission fixes. Metrics are registered per volume type and unregistered on initialization failure or shutdown.

Dependencies and integration points: Used by `OzoneContainer`, `DiskBalancerService`, volume factories, and background health scanning. Configuration sources for locations differ for data, metadata, and DB volumes. Fatal failure escalation goes through `StateContext.getParent().handleFatalVolumeFailures()`.

Risks: `failVolume` itself takes the write lock, and callers such as `handleVolumeFailures` already hold it; this works because the lock is reentrant, but it is important to preserve. Initialization throws if no active volumes exist. Tests should cover partial location failures, tolerated failure thresholds, async callback failure handling, metrics increments/decrements, and fatal-volume callback invocation.
