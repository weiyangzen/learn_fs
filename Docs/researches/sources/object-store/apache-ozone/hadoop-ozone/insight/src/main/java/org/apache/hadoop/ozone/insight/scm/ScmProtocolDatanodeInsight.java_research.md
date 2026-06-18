<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolDatanodeInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolDatanodeInsight.java

Purpose: insight point for SCM's datanode heartbeat/protocol endpoint.

Important APIs: related loggers are `SCMDatanodeProtocolServer` and `StorageContainerDatanodeProtocolServerSideTranslatorPB`. Metrics include common RPC metrics filtered by `servername="StorageContainerDatanodeProtocolService"` and message counters for every `StorageContainerDatanodeProtocolProtos.Type` with prefix `scm_datanode_protocol`.

Control flow and integration: pairs server and translator logs with protocol/RPC metrics to diagnose datanode-to-SCM communication.

State and persistence: stateless. No persistence.

Risks and tests: servername and metric prefix are hardcoded. No direct tests cover this insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolDatanodeInsight.java -->
