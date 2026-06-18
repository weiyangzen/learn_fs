# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestBackgroundContainerDataScanner.java

## Purpose
This suite tests `BackgroundContainerDataScanner`, the per-volume scanner that reads container data and detects corrupt chunks. It validates scan scheduling, unhealthy marking, metrics, checksum update behavior, failed-volume shutdown, clean shutdown during blocked scans, DB-close concurrency, Merkle-tree writing, and "too many open files" suppression.

## Important APIs, types, and functions
The tests call `scanner.runIteration`, `start`, `shutdown`, `isAlive`, and `getMetrics`. They verify `Container.scanData`, `controller.markContainerUnhealthy`, `updateDataScanTimestamp`, `updateContainerChecksum`, `StorageVolumeUtil.onFailure`, and `ContainerDataScannerMetrics`. They use `DataScanResult`, `ContainerScanError`, `FailureType.CORRUPT_CHUNK`, `ContainerMerkleTreeWriter`, `DatanodeStoreSchemaThreeImpl`, and raw table iterators.

## Control flow
The inherited scanner fixture supplies healthy, corrupt-data, corrupt-metadata, open, and deleted containers. Tests manipulate last-scan timestamps to confirm recent containers are skipped and stale/unscanned containers are scanned. Unhealthy detection marks only data-corrupt eligible containers, not open or deleted containers. Failed-volume tests either prevent any iteration from starting or simulate failure mid-iteration, expecting thread termination.

## State and persistence behavior
The scanner updates data-scan timestamps only for containers it scans and writes Merkle-tree checksum data for closed/non-deleted scanned containers. Metrics track iterations, scanned containers, and newly unhealthy containers. The DB-close test opens an iterator inside `scanData`, stops the store concurrently, then releases iteration and expects no exception to escape.

## Dependencies and integration points
The suite integrates scanner scheduling, volume health, controller callbacks, container checksum persistence, metrics registration, RocksDB table iteration, throttling/cancelation parameters, and static volume-failure handling. It contrasts with the metadata scanner by expecting data scanner shutdown when its volume fails.

## Risks and edge cases
Covered risks include rescanning unhealthy containers incorrectly, marking containers unhealthy due only to file-descriptor exhaustion, updating checksums after suppressed scans, hanging on shutdown, crashing when volume failure closes DB resources mid-scan, and continuing data scanning after volume failure.

## Test signals
Signals include Mockito verification of scan methods and controller callbacks, metrics counters, thread liveness checks, `assertDoesNotThrow` around concurrent DB close, and absence of checksum/timestamp updates for suppressed or ineligible containers.
