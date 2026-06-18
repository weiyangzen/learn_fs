# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/VolumeManager.java

Purpose: `VolumeManager` defines read-side volume operations for OM and inherits volume ACL behavior through `IOzoneAcl`.

Important APIs and types: It declares `getVolumeInfo(String volume)` and `listVolumes(String userName, String prefix, String startKey, int maxKeys)`, returning `OmVolumeArgs` records.

Control flow: The interface has no implementation. `VolumeManagerImpl` performs metadata lookups under locks and maps missing volumes to `OMException`.

State and persistence behavior: Implementations read persistent `volumeTable` and user-volume metadata. The interface owns no state.

Dependencies and integration points: OM RPC handlers use this contract to serve volume info/list/ACL requests. It depends on `OmVolumeArgs` and the ACL subsystem.

Risks and test signals: Listing semantics around `startKey`, prefix, maxKeys, and user-null global listing must be consistent with client expectations. Tests should cover missing volumes, ACL access checks, user-filtered lists, and pagination.
