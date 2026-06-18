<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/DatanodeDispatcherInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/DatanodeDispatcherInsight.java

Purpose: insight point for the datanode `HddsDispatcher`, covering requests after Ratis replication.

Important APIs: constructor stores `OzoneConfiguration`. `getDatanodeFromFilter` requires `-f datanode=<host_or_ip>`, reads Ozone HTTP policy, chooses default datanode HTTP or HTTPS port, and returns a `DATANODE` component with host and port. `getRelatedLoggers` returns the `HddsDispatcher` logger at TRACE or DEBUG. `getMetrics` adds `hdds_dispatcher_counter` message counters for every `ContainerProtos.Type`. `filterLog` overrides base behavior to always true.

Control flow and integration: CLI callers must provide a datanode filter so `BaseInsightSubCommand.getHost` can contact that datanode directly. Metrics are fetched from that datanode's `/prom`; logs from `/logstream`.

State and persistence: holds configuration only. No persistence.

Risks and tests: it uses default datanode HTTP ports rather than reading per-node configured HTTP address, so non-default datanode ports require enhancement. The HTTP policy branch chooses HTTP port when HTTP is enabled, even under HTTP_AND_HTTPS. Ignoring filters in `filterLog` means log lines are not additionally scoped by `[datanode=...]`. No direct unit test covers missing filter or port selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/DatanodeDispatcherInsight.java -->
