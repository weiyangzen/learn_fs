<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ContainerReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ContainerReportPublisher.java

Purpose: scheduled full container report publisher for SCM heartbeat state.

Important APIs and control flow: `getReportFrequency` lazily reads and validates the container report interval against heartbeat interval, then adds a random delay up to the interval to avoid synchronized datanode report bursts. `getReport` delegates to `StateContext.getFullContainerReportDiscardPendingICR`, which creates a full report and discards pending incremental container reports.

State and persistence: caches interval only. It refreshes report state in `StateContext` through base publisher behavior.

Dependencies and integration: extends `ReportPublisher`, uses `HddsServerUtil`, Apache Commons `RandomUtils.secure`, and container report protobufs.

Risks and test signals: tests should cover interval validation, random delay bounds, full report generation, and pending ICR discard semantics. Random delay can make scheduler timing tests flaky unless controlled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ContainerReportPublisher.java -->
