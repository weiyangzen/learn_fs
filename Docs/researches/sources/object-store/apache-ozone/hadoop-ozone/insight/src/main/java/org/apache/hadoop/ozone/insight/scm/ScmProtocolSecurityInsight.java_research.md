<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolSecurityInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolSecurityInsight.java

Purpose: insight point for SCM security protocol behavior.

Important APIs: `getRelatedLoggers` adds `SCMSecurityProtocolServerSideTranslatorPB`; it constructs but does not add a `LoggerSource` for `SCMSecurityProtocolServer`. Metrics include common RPC metrics filtered by `servername="SCMSecurityProtocolService"` and message counters for every `SCMSecurityProtocolProtos.Type` under prefix `scm_security_protocol`.

Control flow and integration: used to inspect SCM security RPC traffic and translator logs.

State and persistence: stateless. No persistence.

Risks and tests: missing `loggers.add` for `SCMSecurityProtocolServer` likely drops intended server logs. Description and Javadoc still mention block location, which is misleading. No direct tests catch the logger omission or stale description.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/ScmProtocolSecurityInsight.java -->
