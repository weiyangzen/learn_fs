<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/NodeReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/NodeReportPublisher.java

Purpose: scheduled node report publisher for datanode IO and volume state.

Important APIs and control flow: `getReportFrequency` lazily reads the node report interval and verifies it is at least heartbeat interval. `getReport` navigates from `StateContext` to the parent state machine, container service, and `getNodeReport`.

State and persistence: only cached interval. Reports are pushed to `StateContext` by the base class.

Dependencies and integration: extends `ReportPublisher`, relies on datanode state machine/container report generation and protobuf `NodeReportProto`.

Risks and test signals: tests should cover interval validation, null/failed parent container paths, IO exception propagation to base logger, and correct refresh of full reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/NodeReportPublisher.java -->
