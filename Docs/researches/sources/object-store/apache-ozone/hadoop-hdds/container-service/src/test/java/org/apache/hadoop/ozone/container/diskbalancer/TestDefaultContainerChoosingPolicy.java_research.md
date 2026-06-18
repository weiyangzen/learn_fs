# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDefaultContainerChoosingPolicy.java

## Purpose
Comprehensive tests for `DefaultContainerChoosingPolicy` volume-pair and container selection used by the disk balancer.

## Important APIs, Types, And Functions
Uses `DefaultContainerChoosingPolicy.chooseVolumesAndContainer`, `DiskBalancerVolumeCalculation.getVolumeUsages`, `VolumeFixedUsage`, `ContainerCandidate`, scenario data classes, and `DiskBalancerConfiguration.getMovableContainerStates`.

## Control Flow
Helpers create fixed-usage Hdds volumes, install them into a test volume set, and add containers to a container set. Parameterized scenarios cover imbalance shapes, threshold boundaries, insufficient destination space, one/zero volumes, blocked destinations, in-progress containers, zero-size containers, and expected source/destination ordering. A separate test verifies QUASI_CLOSED eligibility.

## State And Persistence
Temporary volume roots, in-memory volume maps, container sets, container byte stats, committed-byte changes, in-progress container IDs, and delta maps are used.

## Dependencies And Integration Points
Integrates Hdds usage, Ozone container/controller mocks, key-value container data, SCM container size config, disk balancer config, and container state protobuf enums.

## Risks And Edge Cases
The suite encodes detailed balancing math and sorted-index expectations. Formula or boundary changes require updates.

## Test Signals
Candidate nullability, exact source/destination volumes, container ID, sorted indices, lower destination utilization, and movable-state behavior validate selection.
