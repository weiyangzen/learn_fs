# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeSetOwnerRequest.java

Purpose: `OMVolumeSetOwnerRequest` stages changing a volume owner and moving the volume between per-user volume lists.

Important APIs and types: It handles `SetVolumePropertyRequest` with `ownerName`, returns `OMVolumeSetOwnerResponse`, uses `acquireMultiUserLock`, `OmVolumeArgs`, and `PersistedUserVolumeInfo`.

Control flow: `preExecute` stamps modification time and checks WRITE_ACL on the volume. `validateAndUpdateCache` rejects malformed requests without owner name, acquires the volume lock, loads the current owner, returns an OK-status/non-success no-op when the owner is unchanged, acquires both user locks, removes the volume from the old owner, adds it to the new owner, updates volume owner/modification/update ID, and stages all three cache writes.

State and persistence behavior: Successful changes stage old user, new user, and volume table entries. No-op same-owner responses intentionally avoid DB batch mutation. Audit logging happens after lock release.

Dependencies and integration points: It integrates owner-list helpers from `OMVolumeRequest`, OM lock multi-user ordering, volume update metrics, audit maps, and response-side persistence.

Risks and test signals: Risks include missing audit/logging on early same-owner return and correct lock release on partial failures. Tests should cover same-owner no-op, user volume limit on new owner, old/new owner list updates, modification time propagation, and response `success` semantics.
