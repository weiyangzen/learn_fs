# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/DefaultContainerChoosingPolicy.java

## Purpose
`DefaultContainerChoosingPolicy` is the default datanode disk-balancer policy for choosing a source volume, destination volume, and movable container. It is deliberately conservative: it snapshots volume usage, compares fixed effective utilization to an ideal usage plus/minus threshold, then returns a single `ContainerCandidate` only when moving that container will not overfill the selected destination.

## Important APIs and Types
The public API is `chooseVolumesAndContainer(OzoneContainer, MutableVolumeSet, Map<HddsVolume, Long>, Set<ContainerID>, double, Set<State>)`. It implements `ContainerChoosingPolicy` and returns either `ContainerCandidate` or `null`. Internally it uses `DiskBalancerVolumeCalculation.VolumeFixedUsage`, `newVolumeFixedUsage`, `getIdealUsage`, and `computeUtilization` to calculate candidate volume states. A `ThreadLocal<Cache<HddsVolume, Iterator<Container<?>>>>` keeps a per-thread Guava cache of source-volume container iterators with one-hour expiry.

## Control Flow
The method takes a global `ReentrantLock`, obtains an immutable volume list, filters non-positive capacity volumes, sorts by utilization and storage ID, calculates ideal/lower/upper thresholds, and exits early when the highest and lowest utilization volumes already fall within the threshold band. It always uses the highest-utilized volume as source, then tries destination volumes from lowest upward when utilization is lower than the source and usable space is positive. `chooseContainer` walks the cached source iterator and filters containers that are absent from the live container set, already in progress, zero-sized, in a non-movable state, too large for destination usable space, or would push destination utilization past the upper threshold. When a container is selected, the destination volume's committed bytes are incremented by the actual container size before returning.

## State and Persistence
The class persists no durable state. Its mutable state is the provided lock, destination committed-byte reservation, and the thread-local iterator cache. The `deltaMap` is read as a caller-provided transient adjustment to usage. The iterator cache can observe stale containers, so `chooseContainer` revalidates each candidate against `ozoneContainer.getContainerSet()` and invalidates the iterator when exhausted.

## Dependencies and Integration Points
It integrates with `DiskBalancerService` through `ContainerChoosingPolicyFactory` and the disk-balancer configuration default. It depends on `OzoneContainer` for controller/container-set access, `MutableVolumeSet` and `HddsVolume` for volume state, and container protobuf `State` for movability. Tests reference it directly in `TestDefaultContainerChoosingPolicy`, `TestDiskBalancerService`, `TestDiskBalancerTask`, and performance-oriented integration coverage in `TestDiskBalancerPolicyPerformance`.

## Risks and Test Signals
The main risks are stale iterator behavior, reservation accuracy when later movement fails, and threshold edge conditions because the code uses strict `<`/`>` and `>=` comparisons. The global lock limits concurrent decision races, but committed bytes are changed outside durable persistence and must be corrected by the larger disk-balancer workflow. Existing tests cover default policy selection, skipping in-progress containers, movable state filtering, and performance/concurrency scenarios; useful additional signals would include cache-expiry/stale-removal behavior and exact threshold-boundary assertions.
