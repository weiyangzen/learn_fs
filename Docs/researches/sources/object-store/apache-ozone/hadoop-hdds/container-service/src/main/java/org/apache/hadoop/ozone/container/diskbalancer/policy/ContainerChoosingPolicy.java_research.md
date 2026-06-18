# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerChoosingPolicy.java

Purpose: Strategy interface for selecting a source volume, destination volume, and container to move in one disk balancer decision.

Important APIs and types: Declares `chooseVolumesAndContainer(OzoneContainer, MutableVolumeSet, Map<HddsVolume, Long>, Set<ContainerID>, double, Set<State>)`.

Control flow: Implementations are expected to combine volume-pair and container selection, account for in-progress source deltas and container IDs, and reserve destination space only after selecting an actual container.

State and persistence: Interface only; no state. Implementations may hold runtime caches or locks.

Dependencies and integration points: Instantiated by `ContainerChoosingPolicyFactory`; called from `DiskBalancerService.getTasks`; default implementation is `DefaultContainerChoosingPolicy`.

Risks: Contract correctness depends on consistent use of `deltaMap`, `inProgressContainerIDs`, threshold semantics, and movable state filtering. Tests should be written against custom policy implementations if introduced, especially around reservation and null-return behavior.
