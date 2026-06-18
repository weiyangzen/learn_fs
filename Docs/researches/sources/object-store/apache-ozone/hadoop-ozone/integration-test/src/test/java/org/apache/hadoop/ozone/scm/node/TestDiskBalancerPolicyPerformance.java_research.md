# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/scm/node/TestDiskBalancerPolicyPerformance.java

## Purpose
`TestDiskBalancerPolicyPerformance` stress-tests `DefaultContainerChoosingPolicy` with many volumes and containers, verifies disk-full failure behavior, and checks that deleted or in-progress containers are skipped during candidate selection.

## Important APIs, Types, and Functions
The test builds a mock `MutableVolumeSet` with 20 `HddsVolume` instances using `MockSpaceUsageSource`, creates 100,000 `KeyValueContainer` objects in a `ContainerSet`, wraps them in a mocked `OzoneContainer` and `ContainerController`, and invokes `ContainerChoosingPolicy.chooseVolumesAndContainer`. It uses `DiskBalancerVolumeCalculation.getVolumeUsages`, `ContainerCandidate`, `deltaMap`, `inProgressContainerIDs`, and movable states from `DiskBalancerConfiguration`.

## Control Flow, State, and Persistence
`setup` creates volumes with varied utilization, creates containers biased toward high-utilization volumes, marks some containers in progress, and prepares a fixed thread pool. `testVolumeChoosingFailureDueToDiskFull` raises minimum free space so all volumes are effectively full and expects no candidate. `testConcurrentContainerChoosingPerformance` runs 10 threads for 10,000 iterations each, choosing candidates, adding selected IDs to the in-progress set up to a cap, and adjusting source-volume deltas. `testContainerDeletionAfterIteratorGeneration` chooses one container, marks it in progress, removes a second candidate from memory, then expects the policy to return a different valid container.

## Dependencies and Integration Points
This is mostly an in-process policy test integrating datanode volume abstractions, mock space usage, container metadata, container controller iteration, disk balancer calculations, and concurrency structures.

## Risks and Test Signals
Risks include long runtime, high memory use from 100,000 containers, nondeterminism from random utilization and shuffled IDs, and performance output that is informational rather than asserted. Behavioral signals are null candidate under disk-full constraints, no exceptions/failures during concurrent selection, and explicit skipping of in-progress/deleted containers.
