# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestGetClusterTreeInformation.java

Purpose: abstract HA integration test for SCM network topology serialization/deserialization through the block location protocol client.

Important APIs/types/functions: `TestGetClusterTreeInformation` implements `HATests.TestCase`, has `init` and `testGetClusterTreeInformation`. It uses `SCMBlockLocationFailoverProxyProvider`, `ScmBlockLocationProtocolClientSideTranslatorPB`, `StorageContainerManager`, `InnerNode`, and `NetConstants.ROOT`.

Control flow: `@BeforeAll` captures the HA cluster configuration and active SCM from the test harness. The test creates a failover proxy provider, forces the current proxy to the SCM node ID under test, builds the protobuf translator, obtains expected root `InnerNode` from `scm.getClusterMap().getNode(ROOT)`, fetches actual topology via `getNetworkTopology()`, and compares equality.

State and persistence: no own persistence; observes the live SCM cluster map and serialized topology returned over RPC.

Dependencies and integration points: HA cluster harness, SCM block location failover proxy, SCM block location protobuf client, SCM network topology tree, and `InnerNode` equality semantics.

Risks: equality is structural and depends on stable serialization of topology node attributes. The client is not explicitly closed. The test assumes the SCM selected by node ID is reachable and that the cluster map has root populated before the test.

Test signals: exact equality between SCM in-process root topology and RPC-returned topology.
