## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/VolumeArgs.java

### Purpose
`VolumeArgs` is an immutable argument object for creating volumes with optional admin, owner, byte quota, namespace quota, ACLs, and metadata.

### Important APIs and Types
Fields include admin, owner, quota bytes, quota namespace, immutable ACL list, and immutable metadata map. The builder defaults both quotas to `OzoneConsts.QUOTA_RESET`, accumulates metadata and ACLs, and builds a `VolumeArgs`.

### Control Flow
The private constructor copies ACLs and metadata into Guava immutable collections, using empty immutable collections for null inputs. Builder setters simply record values; `addAcl` lazily creates the mutable list and can throw `IOException` because `OzoneAcl` APIs historically expose IO-shaped parsing/creation behavior.

### State and Persistence Behavior
The built object is immutable and local. Volume creation persistence is done by `ObjectStore.createVolume`.

### Dependencies and Integration Points
It integrates with `OzoneAcl`, `OzoneConsts`, Guava immutable collections, and `ObjectStore.createVolume`.

### Risks and Edge Cases
No validation is done for quota values, names, metadata keys, or ACL semantics. Builder remains mutable and can be reused after `build`; previous built instances are protected by immutable copies.

### Test Signals
Tests should verify default quotas, immutable collection behavior, metadata/ACL copy isolation, and propagation into create-volume request conversion.
