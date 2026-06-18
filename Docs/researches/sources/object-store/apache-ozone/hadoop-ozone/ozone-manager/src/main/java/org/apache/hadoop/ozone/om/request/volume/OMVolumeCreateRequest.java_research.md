# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeCreateRequest.java

Purpose: `OMVolumeCreateRequest` validates and stages creation of an Ozone volume, including owner list updates, default ACLs, metrics, audit logging, and object/update IDs.

Important APIs and types: It extends `OMVolumeRequest`, consumes `CreateVolumeRequest` and `VolumeInfo`, builds `OmVolumeArgs`, updates `PersistedUserVolumeInfo`, and returns `OMVolumeCreateResponse`. It uses `USER_LOCK`, `VOLUME_LOCK`, `OmResponseUtil`, `OzoneAclUtil.getDefaultAclList`, and `OMMetrics`.

Control flow: `preExecute` validates the volume name, checks CREATE ACLs when enabled, and sets creation/modification time. `validateAndUpdateCache` builds volume args, acquires volume then user write locks, rejects existing volumes, updates or creates the owner volume list, merges default ACLs depending on `ignoreClientACLs`, stages volume and user table cache entries, and constructs the response.

State and persistence behavior: The request writes user-table and volume-table cache entries with the transaction index. The response later persists both. On success it increments volume counters; on failure it records a create failure metric and does not stage successful mutations.

Dependencies and integration points: It integrates OM ACL checks, volume naming rules, user volume limit enforcement, audit logging, lock tracking, metadata-manager key derivation, and volume response DB batching.

Risks and test signals: Risks include lock-order regressions, duplicate volume races, incorrect ACL merge behavior, and owner-list count limits. Tests should assert cache entries, default ACL behavior, audit on preExecute failure, metric increments, and proper lock release.
