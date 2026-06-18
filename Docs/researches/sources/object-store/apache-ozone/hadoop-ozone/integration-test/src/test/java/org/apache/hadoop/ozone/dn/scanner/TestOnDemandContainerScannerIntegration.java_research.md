# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestOnDemandContainerScannerIntegration.java

Purpose: Integration tests for `OnDemandContainerScanner`, which runs when client interaction or dispatcher write failures expose container corruption.

Important APIs, types, and functions: Extends `TestContainerScannerIntegrationAbstract`. Uses `OnDemandContainerScanner`, `OnDemandScannerMetrics`, `ContainerDispatcher`, `TestContainerCorruptions`, `ContainerLogger`, `ContainerProtos`, `Checksum.getNoChecksumDataProto`, checksum tree readers, and `verifyAllDataChecksumsMatch`. It defines supported corruption sets for closed and open containers based on what the read path can detect.

Control flow: Setup enables scrubbing but disables both background scanners so only on-demand scans can mark corruption. Closed-container tests write and close a key, record initial SCM checksum, corrupt the container, read the key and expect failure, wait for `UNHEALTHY`, validate SCM state/logs, and compare updated checksum behavior. Open-container tests do the same for supported metadata/read-path corruptions on an open container. `testOnDemandScanTriggeredByUnhealthyContainer` builds a synthetic `PutBlock` request for an unwritten chunk, dispatches it directly, asserts failure and unhealthy state, then waits for `lastDataScanTime` and scanner metrics to advance.

State and persistence behavior: On-demand scans update container state, scan time, metrics, checksum files, and SCM replica checksums. Corruptions modify real container files/directories. The dispatcher-trigger test creates no valid block data for the synthetic request but still causes state and metric updates through error handling.

Dependencies and integration points: Links client read failures, dispatcher write failure handling, container-set scan-without-gap behavior, scanner metrics, checksum tree persistence, and SCM unhealthy reports.

Risks: Detection coverage is intentionally limited to paths touched by reads or dispatcher errors; unsupported corruption types are excluded. Timing depends on async scan execution after the read/dispatch failure. Missing metadata/container dir cases cannot write checksum files and require distinct expectations.

Test signals: Read/dispatch failures must occur, local state becomes `UNHEALTHY`, SCM replica state follows, log messages appear, checksum files and data checksum values change only for supported writable cases, and scanner metrics increase after direct dispatcher failure.
