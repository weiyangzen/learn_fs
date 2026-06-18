# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerMetadataScanner.java

## Purpose
This suite tests `BackgroundContainerMetadataScanner`, the process-level scanner for container metadata. It validates timestamp-based scheduling, unhealthy metadata detection, metrics, failed-volume skipping without scanner shutdown, shutdown during a blocked metadata scan, and suppression of "too many open files" metadata-only failures.

## Important APIs, types, and functions
The tests call `scanner.runIteration`, `start`, `shutdown`, `isAlive`, and `getMetrics`. They verify `Container.scanMetaData`, `controller.markContainerUnhealthy`, `StorageVolumeUtil.onFailure`, and `ContainerMetadataScannerMetrics`. They use `MetadataScanResult`, `ContainerScanError`, `FailureType.CORRUPT_CONTAINER_FILE`, and shared `TestContainerScannersAbstract` fixtures.

## Control flow
Recent containers are skipped, stale and unscanned containers are scanned, and scanner metrics are checked after a single iteration. Metadata corruption is expected to mark `openCorruptMetadata` unhealthy, while data corruption alone is not detected by this scanner. Rescan tests first transition a mock container to unhealthy, then run another iteration and confirm metrics do not double-count newly unhealthy containers.

## State and persistence behavior
Unlike the data scanner, this scanner does not update container checksums, so an injected `updateContainerChecksum` failure must not affect metadata-scanner behavior. When the backing volume is failed, queued containers on that volume are skipped, metrics record no scanned/unhealthy containers, but the metadata scanner thread remains alive until explicitly shut down.

## Dependencies and integration points
The file integrates metadata scanning, global scanner lifecycle, volume health checks, controller unhealthy marking, metrics registration/unregistration, and static volume failure notification. It shares abstract scanner fixtures with the data scanner but asserts different policy decisions.

## Risks and edge cases
Risks include treating data corruption as metadata corruption, shutting down the whole metadata scanner because one volume failed, marking containers unhealthy during file-descriptor exhaustion, double-counting unhealthy metrics on rescan, and failing to unregister metrics on shutdown.

## Test signals
Signals are method invocation counts on `scanMetaData` and `markContainerUnhealthy`, metrics values, metrics-system source registration checks, scanner liveness after failed-volume encounter, and explicit non-invocation of unhealthy marking for too-many-open-files-only results.
