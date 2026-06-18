# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeDeleteRequest.java

Purpose: `OMVolumeDeleteRequest` validates and stages deletion of an empty, unreferenced volume and removal of that volume from its owner list.

Important APIs and types: It handles `DeleteVolumeRequest`, uses `OMVolumeRequest.getVolumeInfo` and `delVolumeFromOwnerList`, returns `OMVolumeDeleteResponse`, and updates `PersistedUserVolumeInfo`.

Control flow: `preExecute` checks DELETE ACLs for the volume. `validateAndUpdateCache` increments delete metrics, acquires the volume lock, loads volume metadata, rejects nonzero reference count, acquires the owner user lock, checks `isVolumeEmpty`, removes the volume from owner state, stages user-table update and volume-table tombstone, and builds a delete response.

State and persistence behavior: Successful deletion writes a new owner volume list and a null cache value for the volume key. The response persists deletion from volume table and owner table update. Metrics decrement volume count only on success.

Dependencies and integration points: It integrates reference-count protection for tenant/features, volume emptiness checks, ACL/audit, user and volume locks, and metadata cache-to-response persistence.

Risks and test signals: A notable risk is owner-key consistency: the code obtains `dbUserKey` but reads `getUserTable().get(owner)`, so tests should ensure table API expectations match real keys. Other tests should cover referenced volume denial, nonempty volume denial, owner list mutation, tombstone persistence, and audit on ACL failures.
