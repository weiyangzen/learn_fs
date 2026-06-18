<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureSubCommandUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureSubCommandUtil.java

Purpose: Utility methods for reconfiguration command proxy creation, bounded parallel execution, and discovery of live in-service datanode client RPC addresses.

Important APIs and types: `ReconfigureProtocolClientSideTranslatorPB`, `NetUtils.createSocketAddr`, `UserGroupInformation`, `OzoneConfiguration`, `ExecutorService`, `AtomicInteger`, `ScmClient.queryNode`, `DatanodeDetails`, `Port.Name.CLIENT_RPC`, `NodeOperationalState.IN_SERVICE`, and `HddsProtos.NodeState.DEAD`.

Control flow: `getSingleNodeReconfigureProxy` builds a new configuration, current user, socket address, and protocol translator. `parallelExecute` submits one task per node, calls the supplied operation with `NodeType.DATANODE`, counts successes/failures, waits up to three minutes, and prints summary counts. `getAllOperableNodesClientRpcAddress` queries SCM for IN_SERVICE nodes, skips DEAD nodes, extracts CLIENT_RPC ports, and logs missing ports.

State and persistence behavior: No persistence. Runtime counters track batch results; remote state is changed only by the supplied operation.

Dependencies and integration points: Central dependency for all reconfig subcommands and the parent command's datanode batch mode.

Risks: `parallelExecute` hardcodes `DATANODE` node type and only waits three minutes total. It does not throw on timeout. Missing client RPC ports only print a message. It creates a new default `OzoneConfiguration` for single-node proxy creation rather than using root command config.

Test signals: Proxy address parsing, batch success/failure counting, timeout/interruption behavior, skipping DEAD nodes, missing CLIENT_RPC handling, and address formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureSubCommandUtil.java -->
