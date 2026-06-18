<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/PipelineReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/PipelineReportPublisher.java

Purpose: scheduled pipeline report publisher for SCM heartbeat state.

Important APIs and control flow: `getReportFrequency` lazily reads the configured pipeline report interval, ensures it is not below heartbeat interval, and adds a random delay up to the interval to reduce report synchronization. `getReport` delegates to the container service pipeline report.

State and persistence: caches interval. No direct persistence.

Dependencies and integration: extends `ReportPublisher`, uses `StateContext` parent container service, `PipelineReportsProto`, `HddsServerUtil`, and secure random delay.

Risks and test signals: tests should assert interval validation, random delay bounds, and that pipeline reports are refreshed as full reports by the base publisher. Random delay should be isolated in scheduler tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/PipelineReportPublisher.java -->
