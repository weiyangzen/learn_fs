# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/policy/ContainerCandidate.java

Purpose: Immutable result object returned by disk balancer container selection.

Important APIs and types: Stores `ContainerData`, source `HddsVolume`, and destination `HddsVolume`; exposes getters for each.

Control flow: No logic beyond construction and field access.

State and persistence: Runtime selection result only. It is not persisted directly.

Dependencies and integration points: Returned by `ContainerChoosingPolicy.chooseVolumesAndContainer`, consumed by `DiskBalancerService.getTasks` to create a `DiskBalancerTask`.

Risks: Constructor does not validate non-null fields, so policy implementations must avoid returning incomplete candidates. Tests should cover candidate field propagation and service behavior when policy returns null versus a valid candidate.
