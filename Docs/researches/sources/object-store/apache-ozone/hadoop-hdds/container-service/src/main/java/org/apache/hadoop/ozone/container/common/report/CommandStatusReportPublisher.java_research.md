<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/CommandStatusReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/CommandStatusReportPublisher.java

Purpose: scheduled publisher for command status reports sent to SCM in datanode heartbeats.

Important APIs and control flow: `getReportFrequency` lazily reads the command status report interval, verifies it is not lower than SCM heartbeat interval, and caches it. `getReport` iterates the `StateContext` command status map, adds every status to a `CommandStatusReportsProto`, removes non-PENDING entries from the map, and returns null if no statuses are present.

State and persistence: maintains cached interval. Mutates the shared command status map by draining completed or failed statuses after reporting.

Dependencies and integration: extends `ReportPublisher`, uses `StateContext.getCommandStatusMap`, `CommandStatus`, and protobuf `CommandStatusReportsProto`.

Risks and test signals: map iteration plus removal depends on the map supporting concurrent removal; tests should use the real map type. Frequency validation, empty report returning null, pending retention, executed/failure removal, and duplicate report avoidance should be covered.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/CommandStatusReportPublisher.java -->
