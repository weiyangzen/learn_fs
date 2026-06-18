## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanHelper.java

Purpose: Shared scanner logic used by background and on-demand scanners for deciding whether to scan, running metadata/data scans, updating checksums/timestamps, handling unhealthy results, and triggering volume scans.

Important APIs and functions: `withScanGap()` and `withoutScanGap()` create helpers. `scanData()` checks eligibility, runs `container.scanData()`, handles deleted/transient results, updates container checksum, marks unhealthy if needed, increments metrics, and updates data scan timestamp. `scanMetadata()` performs metadata-only logic. `handleUnhealthyScanResult()` suppresses transient file-descriptor failures, marks containers unhealthy, increments metrics, and calls `triggerVolumeScan()`. `shouldScanMetadata()` and `shouldScanData()` enforce null, failed-volume, min-gap, and container eligibility checks.

Control flow and state: The helper holds logger, controller, metrics, and min scan gap. Recent scan detection compares current time with optional last data scan time. Transient "Too many open files" errors are identified by `ScanTransientIOUtil` and do not mark containers unhealthy or update completion metrics.

Persistence and dependencies: Data scans can persist container checksum updates and data scan timestamps through `ContainerController`. Unhealthy marking persists container state through handlers. Volume scan trigger reports volume failure via `StorageVolumeUtil.onFailure()`.

Risks: Metadata scans also use last data scan time for min-gap suppression. A checksum update failure is logged but does not prevent unhealthy marking or scan completion accounting. Transient failure classification controls whether corruption is ignored. `triggerVolumeScan()` intentionally marks the volume suspect when a container is corrupt.

Test signals: Null/failed-volume/recent scan skips, open container metadata-only on demand, data scan deleted result, transient FD exhaustion, checksum update success/failure, unhealthy marking already unhealthy versus newly unhealthy, timestamp update, metrics increments, and volume scan trigger.
