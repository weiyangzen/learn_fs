# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeSetOwnerResponse.java

Purpose: Tests `OMVolumeSetOwnerResponse` persistence when a volume owner changes and when a failed set-property response is replayed. Important APIs and types include `OMVolumeCreateResponse`, `OMVolumeSetOwnerResponse`, `OmVolumeArgs`, `PersistedUserVolumeInfo`, `Table.KeyValue`, and set-volume-property `OMResponse`.

Control flow: The success test creates an initial volume for `user1`, constructs new owner metadata for `user2`, stages create plus owner-change responses in one batch, commits, and then verifies the volume row key/value and the new owner's user-volume row. The no-op test uses `VOLUME_NOT_FOUND`, calls `checkAndUpdateDB`, and expects the volume table to stay empty.

State and persistence behavior: The response updates `volumeTable` and transitions ownership metadata in `userTable`, including removal or replacement of old-owner volume state. Integration points are owner/admin fields in `OmVolumeArgs`, user-volume protobuf persistence, and OM response batch replay.

Risks: Assertions focus on the new owner and table count; they do not separately assert old-owner row absence. Test signals are the exact volume key, updated `OmVolumeArgs`, new-owner user list, and zero rows for failed replay.
