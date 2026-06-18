# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeChoosingUtil.java

Purpose: Package-private helper methods shared by volume choosing policies.

Important APIs and types: `throwDiskOutOfSpace(AvailableSpaceFilter, Logger)` builds and logs a detailed `DiskOutOfSpaceException`; `logIfSomeVolumesOutOfSpace` emits debug diagnostics when the filter saw at least one full volume.

Control flow: The throw helper includes `filter.mostAvailableSpace()` in the message and logs both message and filter detail before throwing. The logging helper is gated by debug level and `foundFullVolumes`.

State and persistence: Stateless utility class.

Dependencies and integration points: Used by `CapacityVolumeChoosingPolicy` and `RoundRobinVolumeChoosingPolicy` after applying `AvailableSpaceFilter`.

Risks: The utility's usefulness depends on `AvailableSpaceFilter` accurately tracking candidate and rejected volumes during predicate calls. Tests should verify exception contents and debug logging conditions around mixed eligible/ineligible volume sets.
