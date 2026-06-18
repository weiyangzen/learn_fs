# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/CapacityVolumeChoosingPolicy.java

Purpose: Implements the default `VolumeChoosingPolicy` for new container placement on datanode HDDS volumes. It uses a "power of two random choices" strategy: filter volumes that can fit `maxContainerSize`, sample two candidates, then choose the one with more effective available space.

Important APIs and types: `chooseVolume(List<HddsVolume>, long)` is the public policy method. The constructor accepts a shared `ReentrantLock`; the visible-for-testing constructor creates a private lock. It depends on `AvailableSpaceFilter`, `HddsVolume.getCurrentUsage()`, `HddsVolume.getCommittedBytes()`, `HddsVolume.incCommittedBytes()`, and `VolumeChoosingUtil` helpers.

Control flow: empty input throws `DiskOutOfSpaceException`. The method filters volumes under the lock, throws with the best observed available-space detail if no volume can satisfy the request, logs partial out-of-space conditions, and either picks the sole surviving volume or samples two indexes from the filtered list. After choosing, it reserves the requested bytes by incrementing committed bytes before returning.

State and persistence: The class itself persists no state, but it mutates per-volume in-memory reservation state through `committedBytes`. That reservation is meant to protect later writes from overcommitting capacity while open containers are being created or filled.

Dependencies and integration points: Created by `VolumeChoosingPolicyFactory`, used by datanode container allocation paths through `VolumeChoosingPolicy`. It shares the same reservation lock with disk balancer container selection so normal allocation and balancing do not race destination reservations.

Risks: The random policy favors low utilization probabilistically, not deterministically. Correctness depends on callers decrementing committed bytes elsewhere when a reservation is consumed or abandoned. Tests should cover empty volume sets, all-full volume sets, single eligible volume, two-volume bias, and concurrent selection under the shared lock.
