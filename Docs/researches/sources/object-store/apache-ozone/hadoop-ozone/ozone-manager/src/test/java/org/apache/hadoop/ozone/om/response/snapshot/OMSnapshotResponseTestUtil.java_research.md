# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotResponseTestUtil.java

Purpose: Shared utility for snapshot create/delete response tests to seed volume and bucket metadata.

Important APIs/types/functions: Defines final utility `OMSnapshotResponseTestUtil` with static `addVolumeBucketInfoToTable(OMMetadataManager,String,String)`. Uses `OmVolumeArgs`, `OmBucketInfo`, `CacheKey`, `CacheValue`, `volumeTable`, and `bucketTable`.

Control flow: The helper builds volume args and bucket info, computes DB keys, adds cache entries with update IDs, and also writes the rows directly with `put`.

State/persistence: Seeds both cache and backing table rows for volume and bucket so snapshot response tests can perform volume/bucket ID and key-prefix lookups.

Dependencies/integration: Used by snapshot create/delete tests where deleted-dir table cleanup needs FSO bucket key prefixes or snapshot create response needs existing bucket metadata.

Risks/test signals: The helper writes minimal volume/bucket objects without explicit object IDs, relying on metadata manager behavior for IDs. Constructor throws to enforce utility-only use.
