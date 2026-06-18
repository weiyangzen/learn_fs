# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ImmutableVolumeSet.java

Purpose: Simple immutable `VolumeSet` implementation for fixed collections of volumes, mainly useful when callers need the `VolumeSet` interface without mutable maps or locks.

Important APIs and types: Constructors accept varargs or collections of `StorageVolume`. `getVolumesList` returns the immutable list. `checkAllVolumes` delegates to `StorageVolumeChecker`. Lock methods are no-ops.

Control flow: Disk checks are synchronous through `StorageVolumeChecker.checkAllVolumes`; interruption is converted to `IOException` while preserving interrupt status.

State and persistence: Holds only an immutable in-memory list. It does not manage failed-volume maps or metrics.

Dependencies and integration points: Implements `VolumeSet` and can be used with `StorageVolumeChecker` wherever a stable volume collection is enough.

Risks: No lock enforcement means callers must not expect mutation coordination. It also does not remove failed volumes after checks; it only delegates and lets exceptions propagate. Tests should cover immutable copy behavior and interrupted check handling.
