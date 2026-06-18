<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientManager.java

Purpose: Tests `XceiverClientManager` cache identity, reference counting, eviction, close semantics, and retry-failure invalidation against a real non-HA MiniOzoneCluster.

Important APIs and types: Uses `NonHATests.TestCase`, `StorageContainerLocationProtocolClientSideTranslatorPB.allocateContainer`, `XceiverClientManager`, `ScmClientConfig`, `XceiverClientSpi`, Guava `Cache`, `ClientTrustManager`, and `ContainerProtocolCalls.createContainer`. It varies `OZONE_SECURITY_ENABLED_KEY` and cache max size.

Control flow: `BeforeAll` obtains the cluster's storage-container-location client. Tests allocate containers with different replication factors, acquire clients, inspect refcounts, release with normal or invalidating flags, force cache eviction via max size one, and attempt container operations on retained or closed client references.

State and persistence behavior: Durable cluster state includes allocated containers and pipelines. Runtime state is the client cache keyed by pipeline ID plus replication type, each client's refcount, and whether release closes or invalidates the cached connection. Temporary metadata directories isolate security-enabled and non-security client managers.

Dependencies and integration points: Covers the client manager contract between OM/SCM client code, SCM container allocation, xceiver protocol operations, TLS trust-manager plumbing, and cache eviction. It relies on the non-HA cluster fixture for live datanode transport.

Risks: Cache-key construction is duplicated in assertions, so key-format changes require test updates. Some old client handles remain usable while referenced after eviction, so the test is sensitive to the intended distinction between cache membership and object lifetime. Cleanup releases an old duplicate reference after invalidation, which protects against leaked refcounts.

Test signals: Signals include identical client objects for repeated pipeline acquisition, refcount transitions 1 to 2 to 0, cache size zero after invalidating releases, evicted entries absent from the cache, successful use of a referenced-but-evicted client, `Client is closed` after final release, and new cache entries surviving release of stale invalidated clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestXceiverClientManager.java -->
