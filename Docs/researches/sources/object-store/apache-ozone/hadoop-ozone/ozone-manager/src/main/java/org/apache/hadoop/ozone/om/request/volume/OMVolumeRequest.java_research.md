# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/volume/OMVolumeRequest.java

Purpose: `OMVolumeRequest` is the base class for volume requests and centralizes owner-volume-list and volume-table helper logic.

Important APIs and types: It extends `OMClientRequest`. Key helpers are `addVolumeToOwnerList`, `delVolumeFromOwnerList`, `createVolume`, and `getVolumeInfo`. It uses `PersistedUserVolumeInfo`, `OmVolumeArgs`, `CacheKey`, `CacheValue`, and `OMException`.

Control flow: Add/delete owner-list helpers copy existing protobuf lists, enforce max volume count on add, preserve or initialize object IDs, and set update IDs. `createVolume` stages user and volume cache entries. `getVolumeInfo` resolves the volume DB key and throws `VOLUME_NOT_FOUND` if absent.

State and persistence behavior: Helpers only stage cache updates; persistence is completed by response classes during DB batch application. Owner list entries use transaction index as update ID and new-object ID when creating a first list.

Dependencies and integration points: All concrete volume create/delete/owner/quota/ACL requests reuse this class for consistent metadata-manager keying and exceptions.

Risks and test signals: Risks include unordered owner volume names because add uses `HashSet`, max count boundary behavior, and correct object/update ID preservation. Tests should cover null owner lists, deletion from missing owner, duplicate add idempotence, and cache key correctness.
