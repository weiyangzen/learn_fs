## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerDataScanner.java

Purpose: Per-volume background scanner that performs full data scans of containers on one HDDS volume with bandwidth throttling and cancellation.

Important APIs and functions: The constructor binds a volume, controller, throttler, canceler, metrics, and `ContainerScanHelper`. `scanContainer()` shuts down if the volume failed, otherwise delegates to `scanHelper.scanData()`. `getContainerIterator()` returns containers for the volume. `shutdown()` cancels the throttler/canceler and stops the base scanner. Nested `HddsDataTransferThrottler` increments byte-scan metrics.

Control flow and state: One daemon scanner thread runs per volume via the base class. Volume failure triggers scanner shutdown. Throttler methods are synchronized and count bytes before delegating to Hadoop throttling.

Persistence and dependencies: Data scans can update container checksums, scan timestamps, and unhealthy state through `ContainerScanHelper` and `ContainerController`. Depends on `HddsVolume`, `DataTransferThrottler`, `Canceler`, and data scanner metrics.

Risks: A failed volume stops its scanner permanently. Canceling during shutdown depends on scan code observing the canceler. Metrics count requested throttled bytes, not necessarily successfully read bytes. The scanner uses configured minimum scan gaps through the helper.

Test signals: Per-volume iterator filtering, shutdown on failed volume, throttling byte metrics, canceler interruption, scan gap behavior, checksum/timestamp update after data scan, and thread shutdown/join.
