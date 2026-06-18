<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/OmProtocolInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/OmProtocolInsight.java

Purpose: insight point for the Ozone Manager client RPC endpoint.

Important APIs: `getRelatedLoggers` returns the `OzoneManagerProtocolServerSideTranslatorPB` logger for OM. `getMetrics` adds common RPC metrics filtered by `servername="OzoneManagerService"` and protocol message counters for every `OzoneManagerProtocolProtos.Type` under prefix `om_client_protocol`. `getDescription` identifies the OM RPC endpoint.

Control flow and integration: combines Hadoop RPC metrics and generated OM protobuf enum values for broad operation coverage. Used by `metrics` and `log` subcommands.

State and persistence: stateless. No persistence.

Risks and tests: servername and metric prefix are hardcoded. If RPC server metric tags change, metrics will print `???`. No direct tests cover this insight point.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/om/OmProtocolInsight.java -->
