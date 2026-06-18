## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOnDemandContainerScanner.java

Purpose: Concrete test suite for `OnDemandContainerScanner`, exercising asynchronous single-container scans, deduplication, metrics, shutdown, checksum updates, unhealthy marking, and volume-failure behavior.

Important APIs/types/functions: `OnDemandContainerScanner.scanContainer`, `scanContainerWithoutGap`, `shutdown`, `OnDemandScannerMetrics`, `ContainerController.markContainerUnhealthy`, `updateDataScanTimestamp`, `updateContainerChecksum`, `DataTransferThrottler`, `Canceler`, and inherited fixtures from `TestContainerScannersAbstract`.

Control flow: Setup constructs the scanner from shared config/controller. Tests submit scans, wait on returned `Future`s when present, and verify scanner behavior. Duplicate tests block `scanData`/`scanMetaData` behind latches and assert the second scheduling returns `Optional.empty`. Shutdown tests interrupt a long scan and ensure no false unhealthy mark. Rescan tests move a mock container into `UNHEALTHY` and verify subsequent scans count differently.

State and persistence behavior: Maintains scanner executor state, in-flight container IDs, metrics source registration in `DefaultMetricsSystem`, scan timestamps, and checksum update calls. No real persistence, but controller calls model persisted timestamp/checksum writes.

Dependencies and integration points: Integrates scanner result classes, container controller, metrics system, volume failure flags, and logging (`LogCapturer`) for volume scan trigger messages.

Risks and test signals: Strong concurrency signal for duplicate suppression and shutdown interruption. Wall-clock scan-gap tests can be timing-sensitive. The timestamp test appears to rescan `healthy` while verifying `deletedContainer` timestamp was never updated, relying on fixture behavior rather than directly scanning deleted first.
