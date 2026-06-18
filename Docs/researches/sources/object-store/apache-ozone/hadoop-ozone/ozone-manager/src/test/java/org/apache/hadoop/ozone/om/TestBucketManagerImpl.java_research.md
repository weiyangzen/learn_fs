<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketManagerImpl.java

Purpose: Tests core `BucketManagerImpl` behavior through a real test OM and RPC write client.

Important APIs/types/functions: Uses `OmTestManagers`, `OzoneManagerProtocol`, `BucketManager`, `OMMetadataManager`, `OmBucketInfo`, `OmBucketArgs`, `OmVolumeArgs`, `OmKeyArgs`, `OpenKeySession`, bucket encryption helpers, EC/default replication configs, and `OMRequestTestUtils.addBucketToOM`.

Control flow: Setup creates a temp OM. Helpers create sample volumes and direct bucket DB entries. Tests cover bucket creation without volume, encrypted bucket creation with mocked KMS metadata, normal creation, duplicate creation, invalid bucket lookup, `getBucketInfo` volume/bucket error paths, storage type update, versioning update, delete bucket, non-empty bucket deletion after opening/committing keys, and linked bucket resolution across a two-hop link chain.

State and persistence behavior: Mutates real OM metadata through RPC and direct test utility writes. Validates bucket table state, encryption key info, storage type, versioning, delete removal, key/open-key state effects on bucket emptiness, and resolved link-bucket inherited properties.

Dependencies and integration points: Integrates OM startup, write-client protocol, volume/bucket/key managers, KMS provider injection, SCM block fake, bucket layout, quotas, replication, metadata, and link bucket resolution.

Risks: Tests mix RPC operations and direct metadata insertion, which can bypass validation/cache paths. Cleanup stops OM directly and may not close the RPC client. Assertions depend on exact exception messages. Link-bucket test exercises info resolution but not cyclic links or missing targets.

Test signals: Passing confirms major bucket CRUD/property behaviors, encrypted bucket metadata preservation, non-empty delete protection, and link resolution of target bucket properties.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestBucketManagerImpl.java -->
