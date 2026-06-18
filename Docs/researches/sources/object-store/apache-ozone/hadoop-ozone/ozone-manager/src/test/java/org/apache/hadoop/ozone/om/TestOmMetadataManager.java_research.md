# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmMetadataManager.java

Purpose: Broad unit coverage for `OmMetadataManagerImpl`: table schema coverage, volume/bucket/key listing with cache overlays and pagination, open-file listing, expired open key and MPU discovery, snapshot listing, and multipart upload key listing.

Important APIs and types: `OMMetadataManager`, `OmMetadataManagerImpl`, `OMDBDefinition`, all core table constants, `OmVolumeArgs`, `OmBucketInfo`, `OmKeyInfo`, `OmMultipartKeyInfo`, `OpenKeySession`, `ListOpenFilesResult`, `SnapshotInfo`, `ListSnapshotResponse`, `BucketLayout`, `CacheKey`, `CacheValue`, `TransactionInfo`, and `OMRequestTestUtils`.

Control flow: setup creates a temp RocksDB metadata manager. Tests seed rows either through DB helpers or direct table cache entries, then call listing APIs with prefixes, start markers, and limits. Volume and bucket tests validate sorted traversal. Key tests cover pure cache, cache+DB, delete markers, and pagination. Parameterized open-key tests cover default and FSO layouts. Expiration tests create old open keys or MPUs based on configured thresholds and verify limit behavior. Snapshot tests seed snapshots across prefixes and buckets and validate path checks. Multipart upload key tests interleave table and cache rows and check marker behavior.

State and persistence: this file exercises both persisted RocksDB tables and unflushed table caches. It writes transaction info, volumes/users, buckets, keys, open keys/open files, multipart info and parts, snapshot info, and table definitions. Cache deletion entries are used to ensure in-memory tombstones override DB rows.

Dependencies and integration points: integrates OM metadata naming conventions for DB keys, bucket layouts, snapshot chain/listing expectations, cleanup-service selectors for expired open keys/MPUs, and generated table definitions. It is a high-signal contract for Recon, cleanup services, S3 MPU flows, and client list APIs.

Risks and edge cases: prefix/start marker arithmetic is easy to break because cache and DB iterators must merge without duplicates; deleted cache entries must hide persisted keys; expired open key logic must exclude MPU-related entries even when legacy `isMultipartKey` flags are false; MPU expiration limits are by part count and round to whole uploads; snapshot listing must not leak snapshots from other buckets; `getMultipartUploadKeys` uses `maxUploads + 1` sentinel behavior unless no-pagination is requested.

Test signals: exact counts for list volumes/buckets/keys/snapshots, equality with `TreeSet`/`TreeMap` expected ordering, exception result codes for missing volume/bucket snapshot paths, complete table-name equality with `OMDBDefinition`, expired item name containment, and all-MPU key listing across mixed cache/DB rows.
