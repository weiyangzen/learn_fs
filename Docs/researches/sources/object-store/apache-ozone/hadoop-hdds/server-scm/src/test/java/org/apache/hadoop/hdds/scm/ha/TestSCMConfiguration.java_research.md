<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMConfiguration.java

Purpose: This suite validates SCM HA configuration expansion, node-specific address/port keys, default Ratis log appender settings, and shared-port configuration behavior.

Important APIs and types: It uses `OzoneConfiguration`, `SCMHANodeDetails.loadSCMHAConfig`, `SCMStorageConfig`, `SCMNodeDetails`, `ScmRatisServerConfig`, `RatisUtil.newRaftProperties`, `ConfUtils.addKeySuffixes`, `NetUtils`, `HddsServerUtil`, and multiple `ScmConfigKeys`.

Control flow: `testSCMConfig` configures one SCM service with three nodes and per-node client, block, datanode, security, HTTP, DB, SCM address, and Ratis port keys. After loading HA config, it verifies node `scm1` values remain in the expected suffixed keys and confirms Ratis log appender min wait is zero both in SCM config and generated Raft properties. `testSamePortConfig` sets shared global ports, loads HA details, and verifies local and peer node details use the shared addresses and ports.

State and persistence behavior: Configuration state is in memory. A temp metadata directory is used only as a config value; no persistent SCM DB is initialized.

Dependencies and integration points: This protects HA config parsing used during SCM startup and port binding, including security service address resolution outside `SCMHANodeDetails`.

Risks: The tests are exact about default ports and key suffix behavior. Any intentional config fallback change must update the assertions.

Test signals: Exact config values, socket addresses, local/peer Ratis and gRPC ports, security address from `HddsServerUtil`, and zero Ratis log appender wait duration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMConfiguration.java -->
