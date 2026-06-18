# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeSet.java

Purpose: Minimal interface for a collection of `StorageVolume` objects with read/write locking and health-check delegation.

Important APIs and types: Extends `ReadWriteLockable`; declares `getVolumesList` and `checkAllVolumes(StorageVolumeChecker)`.

Control flow: Implementations decide whether locks are active (`MutableVolumeSet`) or no-op (`ImmutableVolumeSet`) and how failed checks are handled.

State and persistence: Interface only; no state.

Dependencies and integration points: Used by `StorageVolume`, `StorageVolumeChecker`, `MutableVolumeSet`, `ImmutableVolumeSet`, and code that wants a common abstraction over active volume collections.

Risks: The interface does not specify whether returned lists are mutable, snapshots, or live views; callers must rely on implementation behavior. Tests should target concrete implementations and call sites that assume snapshot semantics.
