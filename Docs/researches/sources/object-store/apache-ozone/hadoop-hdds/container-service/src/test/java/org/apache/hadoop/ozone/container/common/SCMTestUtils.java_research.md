## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/SCMTestUtils.java

Purpose: `SCMTestUtils` provides test helpers for starting mock SCM RPC servers and building datanode test configurations.

Important APIs and functions: helpers include `startScmRpcServer` overloads, private `startRpcServer`, `getReuseableAddress`, `getConf`, `getOzoneConf`, `getReplicationType`, and `getReplicationFactor`. `CLUSTER_ID` is a shared fixed cluster id for tests.

Control flow and state: `startScmRpcServer` converts Ozone configuration to Hadoop configuration, sets `ProtobufRpcEngine` for `StorageContainerDatanodeProtocolPB`, wraps a `StorageContainerDatanodeProtocolServerSideTranslatorPB` in a reflective blocking service, starts the RPC server, and can update `OZONE_SCM_NAMES` to the actual listener address when binding to port zero. `getConf()` creates datanode, metadata, and datanode ID directories and configures mock space usage and test authorization.

Persistence and integration: helpers create temp filesystem directories and live Hadoop RPC servers. They integrate with `ScmTestMock`, PB translators, `ProtocolMessageMetrics`, and RATIS configuration.

Risks and test signals: `getReuseableAddress()` is inherently race-prone, and the newer port-zero overload documents avoiding that TOCTOU race. Tests using live RPC must shut servers down. Replication type/factor helpers mirror the RATIS enabled flag.
