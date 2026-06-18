## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestContainerScannersAbstract.java

Purpose: Abstract JUnit/Mockito base for container scanner test classes, defining the behavioral contract every scanner implementation must satisfy: scan-gap skipping, previously/unscanned handling, unhealthy detection, metrics, shutdown, volume failure, checksum update failure, and volume-scan triggering.

Important APIs/types/functions: `TestContainerScannersAbstract`, mocked `Container<ContainerData>` fixtures (`healthy`, `openContainer`, `openCorruptMetadata`, `corruptData`, `deletedContainer`), `ContainerScannerConfiguration`, `ContainerController`, `setScannedTimestampOld`, `setScannedTimestampRecent`, `verifyContainerMarkedUnhealthy`, `mockKeyValueContainer`, and `setContainers`. `mockContainerController` wires test fixtures through `ContainerTestUtils.setupMockContainer`.

Control flow: `setup` creates lenient mocks, enables scanning, sets scan intervals to zero, and installs a mock controller. Timestamp helpers force data scan eligibility around `CONTAINER_SCAN_MIN_GAP_DEFAULT`. `mockKeyValueContainer` uses a real `KeyValueContainer.shouldScanData` call on a Mockito mock to exercise concrete container-state filtering. `setContainers` changes controller iteration results for volume and global scans.

State and persistence behavior: Maintains an in-memory collection returned by controller mocks and an `AtomicLong` sequence for stable unique container IDs. No disk persistence occurs except mocked volume path exposure.

Dependencies and integration points: Depends on Ozone container scan result helpers, `HddsVolume`, key-value container data, JUnit abstract tests, and Mockito verification modes. Subclasses inherit required test methods and shared fixture state.

Risks and test signals: Lenient Mockito can mask unused or stale stubbing. Timestamp tests depend on wall-clock `Instant.now`. The file is a high-value signal for scanner contract regressions because every scanner subclass must implement the same abstract tests.
