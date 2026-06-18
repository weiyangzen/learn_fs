# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/MetadataVolume.java

Purpose: Represents a datanode metadata/Ratis volume. Ozone tracks health and usage for it but does not format it like HDDS data volumes.

Important APIs and types: Extends `StorageVolume`; returns `VolumeType.META_VOLUME`; overrides `format`, `createTmpDirs`, and `getStorageID`. The builder uses an empty storage subdirectory, meaning the configured root is the storage directory.

Control flow: Constructor delegates base initialization and immediately creates tmp/disk-check directories at the volume root. Formatting and later tmp-dir creation are no-ops because metadata volumes are independent of SCM cluster IDs.

State and persistence: It still uses `StorageVolume` usage/check state, but it does not expose a storage ID and should not rely on HDDS VERSION formatting semantics in normal operation.

Dependencies and integration points: Built by `MetadataVolumeFactory` and managed by `MutableVolumeSet` when `META_VOLUME` is selected. Used for Ratis/metadata directory health, not container placement.

Risks: `getStorageID` returning an empty string is intentional but can surprise generic reporting or map-key logic. Tests should verify metadata volumes do not format on cluster registration and that tmp dirs are available immediately.
