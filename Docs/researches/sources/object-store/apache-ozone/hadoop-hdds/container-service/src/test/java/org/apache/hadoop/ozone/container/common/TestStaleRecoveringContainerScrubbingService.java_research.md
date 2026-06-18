# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/TestStaleRecoveringContainerScrubbingService.java

Purpose: This test verifies that `StaleRecoveringContainerScrubbingService` marks old RECOVERING containers UNHEALTHY while leaving CLOSED containers and non-stale RECOVERING containers unchanged.

Important APIs and types: It uses `StaleRecoveringContainerScrubbingService`, `ContainerSet`, `ContainerImplTestUtils.newContainerSet`, `TestClock`, `KeyValueContainerData`, `KeyValueContainer`, `HddsVolume`, `MutableVolumeSet`, `RoundRobinVolumeChoosingPolicy`, and `ContainerTestVersionInfo.ContainerTest`.

Control flow: `initVersionInfo` sets the active layout and schema, then `init` creates a formatted `HddsVolume` under a temp directory and mocks volume selection to return it. `createTestContainers` advances the test clock before each container, creates key-value containers in a requested state, persists them on the volume, and adds them to the container set. The main test creates closed containers, runs the scrubber, creates recovering containers, advances time beyond timeout, runs again, then increases the recovering timeout and proves newer recovering containers remain RECOVERING.

State and persistence behavior: The test persists actual container directories and uses `ContainerSet` creation timestamps driven by `TestClock`. State under test is container state transition from RECOVERING to UNHEALTHY based on age and timeout. It also exercises `ContainerSet.setRecoveringTimeout`.

Dependencies and integration points: It integrates container creation, volume formatting, clock-controlled container metadata, container set iteration, and the background scrubbing service's one-shot `runPeriodicalTaskNow` path. DB caches are shut down after each test.

Risks: The test depends on `newContainerSet(10, testClock)` honoring the injected clock. The service interval and timeout values are small and manually triggered, reducing but not eliminating timing coupling. It does not test service daemon start/stop.

Test signals: Container count remains unchanged, CLOSED containers remain CLOSED, stale RECOVERING containers become UNHEALTHY, and RECOVERING containers younger than the adjusted timeout remain RECOVERING.
