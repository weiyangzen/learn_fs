# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/RoundRobinVolumeChoosingPolicy.java

Purpose: Alternative `VolumeChoosingPolicy` that scans HDDS volumes in round-robin order and returns the first volume with enough usable space for the requested container size.

Important APIs and types: `chooseVolume(List<HddsVolume>, long)` is the policy entry point. It uses `AvailableSpaceFilter`, the shared `ReentrantLock`, `nextVolumeIndex`, and `VolumeChoosingUtil`.

Control flow: Empty input throws `DiskOutOfSpaceException`. The current index is normalized in case the volume list shrank after a failure. Under the lock, the method tests each volume, advances circularly, reserves committed bytes on success, and throws a detailed out-of-space exception after a full loop with no eligible volume.

State and persistence: The only class-local state is `nextVolumeIndex`, which controls future selection fairness. It mutates volume committed bytes but has no durable state.

Dependencies and integration points: Can be configured through `VolumeChoosingPolicyFactory`. Requires callers to pass a volume list that remains consistent for the duration of selection.

Risks: `currentVolumeIndex` is computed before acquiring the policy lock, so list size changes by other mechanisms must still be controlled by caller-side volume-set locking. Tests should cover index wraparound, list shrinkage, out-of-space logging/throwing, and reservation increments.
