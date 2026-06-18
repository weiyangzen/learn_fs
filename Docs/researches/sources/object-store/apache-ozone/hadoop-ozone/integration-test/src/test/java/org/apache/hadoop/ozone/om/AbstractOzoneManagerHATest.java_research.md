# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/AbstractOzoneManagerHATest.java

## Purpose
`AbstractOzoneManagerHATest` is a shared base class for Ozone Manager HA integration tests. It centralizes HA cluster setup, client creation, retry tuning, follower-read toggles, key deleting-service configuration, and common helpers for volume, bucket, key, file, prefix, and failure/quorum assertions.

## Important APIs, Types, and Functions
- `initCluster(boolean followerReadEnabled)` configures ACLs, administrators, client retry limits, IPC retry intervals, Ratis purge/snapshot thresholds, filesystem snapshots, default bucket layout, optional follower reads/local leases, key deletion service settings, and a three-OM HA cluster.
- Accessors expose the cluster, object store, client, configuration, service ID, purge gap, snapshot threshold, retry cache duration, and OM count.
- `createKey(...)`, `createPrefixName()`, and `createPrefix(...)` create reusable OM objects.
- `setupBucket()` creates a volume/bucket and validates owner/admin metadata.
- `linkBucket(...)` creates a linked bucket pointing at a source bucket.
- `createVolumeTest(...)`, `createKeyTest(...)`, and `testCreateFile(...)` execute success/failure-oriented operations and validate results.
- `waitForLeaderToBeReady()` waits for OM leader election.

## Control Flow
Subclasses call `initCluster` before tests. The helper sets configuration, builds `MiniOzoneHAClusterImpl`, waits for readiness, creates a client with follower-read config if requested, and stores the object store. Operation helpers create objects through `ObjectStore` and `OzoneBucket` APIs, then read back metadata/content. Failure helpers catch `IOException`, distinguish `RemoteException`, `ConnectException`, and leader-discovery failures, and assert error text when quorum should be unavailable.

## State and Persistence Behavior
The base class creates persistent HA OM state through Ratis and OM RocksDB. It sets snapshot and log purge thresholds, retry cache duration, and key-deleting limits, so subclass tests inherit deterministic HA and background-service behavior. Created volumes, buckets, keys, linked buckets, and ACL prefixes are persisted in OM metadata.

## Dependencies and Integration Points
The class integrates MiniOzone HA cluster construction, Ozone RPC clients, `OzoneManagerRatisServerConfig`, `OmConfig`, ACL objects, Ozone bucket/key/file APIs, Ratis leader election, and Hadoop IPC retry settings.

## Risks and Test Signals
Risks include static shared state across subclasses, assumptions about exact exception messages, and follower-read configuration impacting client routing. Signals include validated volume/bucket attributes, readable key/file contents, correct `isFile` behavior during listing, and expected failure modes when quorum is absent.
