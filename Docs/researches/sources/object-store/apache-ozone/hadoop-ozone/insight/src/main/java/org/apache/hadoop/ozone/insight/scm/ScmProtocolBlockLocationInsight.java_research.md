<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolBlockLocationInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolBlockLocationInsight.java

Purpose: insight point for the SCM block location protocol endpoint.

Important APIs: related loggers are `ScmBlockLocationProtocolServerSideTranslatorPB` and `SCMBlockProtocolServer`. Metrics include common RPC metrics filtered by `servername="StorageContainerLocationProtocolService"` and message counters for every `ScmBlockLocationProtocolProtos.Type` with prefix `scm_block_location_protocol`.

Control flow and integration: used for protocol-level log streaming and metrics from SCM. It inherits base filter behavior.

State and persistence: stateless. No persistence.

Risks and tests: servername filter appears shared with storage container location service and must match exported tags. No direct tests cover logger list or metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolBlockLocationInsight.java -->
