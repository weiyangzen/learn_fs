# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestDataUtil.java

Purpose: general-purpose Ozone integration-test data factory and metadata cleanup utility for volumes, buckets, keys, linked buckets, and OM tables.

Important APIs/types/functions: overloads of `createVolumeAndBucket`, `createVolume`, `createStringKey`, `createOutputStream`, `createKey`, `readFully`, `getKey`, `createBucket`, `createLinkedBucket`, `createKeys`, `cleanupDeletedTable`, `cleanupOpenKeyTable`, and `lookupOmKeyInfo`. It uses Ozone client APIs, `BucketArgs`, `VolumeArgs`, `DefaultReplicationConfig`, `ReplicationConfig`, `BucketLayout`, `OmKeyArgs`, `OmKeyInfo`, `RepeatedOmKeyInfo`, and OM metadata `Table`.

Control flow: volume/bucket helpers construct storage type DISK and optional bucket layout/default replication, create a random owner/admin volume, then create/get buckets. Random helper retries up to five times on volume/bucket name collisions. Key helpers generate random alphanumeric content or write provided bytes through optional replication config, then read fully or return string content. Linked bucket helper creates a source bucket then a linked bucket with `sourceVolume/sourceBucket`. `createKeys` opens a cluster client, creates a bucket, writes N RATIS ONE keys, and returns OM key info for each. Cleanup helpers iterate deleted/open key tables, collect keys, and delete them while ignoring per-key IOExceptions.

State and persistence: creates real OM metadata entries and key data in the cluster. Cleanup mutates OM metadata tables directly, bypassing normal service flows.

Dependencies and integration points: Ozone object store, OM metadata manager, bucket layouts, replication configs, Apache Commons random strings/IO, Guava maps, and MiniOzoneCluster.

Risks: direct metadata table deletion can leave related state inconsistent if used outside targeted tests. Cleanup silently ignores delete failures. Random names reduce but do not eliminate collisions. `getKey` uses Scanner with whole-stream delimiter, which assumes textual content and non-empty stream.

Test signals: no test methods; downstream tests use it to create reproducible data and assert reads do not throw, returned key info exists, and OM tables can be reset for isolation.
