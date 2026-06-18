# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeDeleteResponse.java

Purpose: Tests `OMVolumeDeleteResponse` batch behavior for deleting a volume and its user-volume mapping. Important APIs and types include `OMVolumeCreateResponse` for setup, `OMVolumeDeleteResponse`, `OMMetadataManager`, `PersistedUserVolumeInfo`, `OmVolumeArgs`, and delete-volume `OMResponse`.

Control flow: The success test stages a volume create and a volume delete in the same batch. The delete response carries an updated empty `PersistedUserVolumeInfo`, then the batch is committed and both volume and user entries are expected to be gone. The no-op path uses failed `VOLUME_NOT_FOUND` status and verifies `checkAndUpdateDB` does not throw.

State and persistence behavior: This exercises deletion from `volumeTable` and removal of the `userTable` row when a user has no remaining volumes. It depends on OM DB key construction for volume/user keys and on ordered batch operations.

Risks: The success path composes create and delete in one batch, so it validates final batch state but not visibility between operations. Test signals are null reads from `volumeTable` and `userTable`, plus no exception for unsuccessful replay.
