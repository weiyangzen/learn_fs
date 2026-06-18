# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyResponse.java

Purpose: Base fixture for key response tests.

Important APIs/types/functions: Provides `omMetadataManager`, `batchOperation`, random `volumeName`, `bucketName`, `keyName`, `replicationConfig`, `omBucketInfo`, `clientID`, `txnLogId`, and helper methods `getOpenKeyName`, `getOmKeyInfo`, `getOzoneConfiguration`, and `getBucketLayout`.

Control flow: `setup` creates a temporary OM DB, opens a batch, initializes identifiers, builds RATIS/ONE replication config, writes volume and bucket cache entries, and stores bucket metadata. `stop` clears Mockito inline mocks and closes the batch.

State/persistence: Seeds volume and bucket metadata through table cache entries; subclasses add concrete open/key/deleted table mutations. The batch is per-test.

Dependencies/integration: Centralizes OM metadata manager setup for key, tagging, prefix ACL, and related response tests.

Risks/test signals: Volume/bucket entries are cache-only in this fixture, which is sufficient for many lookups but differs from fully committed rows. Subclasses must override bucket layout where table choice matters.
