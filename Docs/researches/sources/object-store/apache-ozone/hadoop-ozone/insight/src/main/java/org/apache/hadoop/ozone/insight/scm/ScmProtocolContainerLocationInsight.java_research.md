<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolContainerLocationInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolContainerLocationInsight.java

Purpose: insight point for the SCM container location protocol endpoint.

Important APIs: `getRelatedLoggers` adds `StorageContainerLocationProtocolServerSideTranslatorPB`; it also constructs a `LoggerSource` for `StorageContainerLocationProtocolService` but does not add it to the list. Metrics include common RPC metrics filtered by `servername="StorageContainerLocationProtocolService"` and message counters for every `StorageContainerLocationProtocolProtos.Type` under prefix `scm_container_location_protocol`.

Control flow and integration: metrics and logs are sourced from SCM. The missed `add` means one intended logger is silently omitted.

State and persistence: stateless. No persistence.

Risks and tests: the unadded `LoggerSource` is likely a bug and reduces log coverage. The class Javadoc says block location, which is stale for container location. No direct tests catch the missing logger.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolContainerLocationInsight.java -->
