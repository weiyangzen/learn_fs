## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandContainerScanner.java

Purpose: Provides single-threaded on-demand container scans triggered by failures or explicit requests, with duplicate scheduling suppression and optional scan-gap bypass.

Important APIs and functions: The constructor creates on-demand throttler, canceler, metrics, executor, scheduled-container set, and helpers with/without gap. `scanContainer()` queues a scan subject to min-gap. `scanContainerWithoutGap()` queues regardless of recent scan time. `performOnDemandScan()` chooses data scan when eligible, otherwise metadata scan. `shutdown()` unregisters metrics, cancels scans, shuts down the executor, waits up to five seconds, and force-stops if needed.

Control flow and state: A concurrent key set prevents multiple queued/running scans for the same container ID. The executor is single-threaded, so scans serialize. The scheduled ID is removed after `performOnDemandScan()` returns.

Persistence and dependencies: Scans can update checksums, timestamps, unhealthy state, and volume failure signals through `ContainerScanHelper`. Depends on `ExecutorService`, `Future`, `DataTransferThrottler`, `Canceler`, and on-demand scanner metrics.

Risks: If `performOnDemandScan()` throws an unchecked exception, the scheduled-container ID removal is skipped because it is not in a finally block. `scanContainer()` calls `shouldScanMetadata()` before duplicate suppression, so recent scans return empty without noting an already scheduled scan. Single-threading limits concurrency under many requests.

Test signals: Queue accepted/rejected duplicate scans, scan-gap and no-gap paths, open-container metadata-only behavior, closed/quasi-closed data scan behavior through `shouldScanData()`, unchecked exception cleanup risk, shutdown cancellation, and forced executor shutdown timeout.
