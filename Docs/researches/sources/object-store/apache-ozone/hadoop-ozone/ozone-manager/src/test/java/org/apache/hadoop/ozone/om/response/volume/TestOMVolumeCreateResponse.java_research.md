# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeCreateResponse.java

Purpose: Tests `OMVolumeCreateResponse` persistence for successful and failed CreateVolume responses. Important APIs and types include `OMMetadataManager`, `BatchOperation`, `OmVolumeArgs`, `PersistedUserVolumeInfo`, protobuf `OMResponse`, and `CreateVolumeResponse`.

Control flow: The inherited base test creates a temporary OM RocksDB and batch. The success test builds a random volume, owner user, user-volume list, and successful `OMResponse`, calls `addToDBBatch`, manually commits the batch, and verifies `volumeTable` and `userTable`. The no-op test builds a failed `VOLUME_ALREADY_EXISTS` response, calls `checkAndUpdateDB`, and expects no rows.

State and persistence behavior: The test is specifically about deferred batch writes into `volumeTable` and `userTable`; nothing should be visible as accepted state until `commitBatchOperation`. Dependencies and integration points are OM response replay, metadata table key generation, protobuf status handling, and RocksDB batch semantics.

Risks: The test assumes object equality for `OmVolumeArgs` and `PersistedUserVolumeInfo` is stable and that failed responses do not mutate DB state. Test signals are exact table row counts and matching stored values after commit.
