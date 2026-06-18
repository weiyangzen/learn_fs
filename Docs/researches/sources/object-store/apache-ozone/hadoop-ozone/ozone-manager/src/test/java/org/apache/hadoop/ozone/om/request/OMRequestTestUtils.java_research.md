# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/OMRequestTestUtils.java

Purpose: shared test fixture utility for OM client request tests, providing helpers to seed OM metadata tables/caches and construct protobuf `OMRequest` objects across volume, bucket, key, multipart upload, ACL, tenant, snapshot, FSO, and S3-auth workflows.

Important APIs/types: `OMMetadataManager`, `OmVolumeArgs`, `OmBucketInfo`, `OmKeyInfo`, `OmDirectoryInfo`, `OmMultipartKeyInfo`, `SnapshotInfo`, `OmPrefixInfo`, `CacheKey`, `CacheValue`, `BucketLayout`, `ReplicationConfig`, `OzoneAcl`, `OzoneObjInfo`, and many `OzoneManagerProtocolProtos` request builders.

Control flow: methods are static and grouped by fixture purpose. DB seeders add volumes/buckets/users/keys/directories/snapshots/prefixes to tables and often parallel cache entries. Key helpers branch between open key table and committed key table, update bucket used bytes when possible, and handle OBS/legacy vs FSO path-key formats. Multipart helpers seed open multipart keys, multipart info, parts, and request messages. Request factories build volume property, ACL, MPU, volume create, bucket delete, tenant, S3 volume context, snapshot create/move/rename/delete, and S3-authenticated commit-key requests. Configuration helpers enable FSO paths and install replication config validators on mocked OM.

State and persistence behavior: directly mutates OM DB tables and caches, frequently with synthetic transaction indexes and object IDs from `System.currentTimeMillis()`. Some helpers only add cache entries, while others write both cache and persistent table rows.

Dependencies and integration points: heavily integrated with OM metadata schema, request protobufs, snapshot cleanup tables, FSO object ID path encoding, quota side effects, replication validation, and tests across the OM request package.

Risks: helper behavior can diverge from production request side effects; object IDs based on current time can collide under fast tests; mixed cache/table writes require callers to know visibility expectations.

Test signals: not a test class itself, but it enables broad OM request tests by constructing realistic metadata and protobuf inputs.
