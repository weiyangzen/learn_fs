<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/package-info.java

Purpose: package documentation for datanode report publishing to SCM.

Important APIs and control flow: no executable code. The documentation explains that datanode state is split into multiple heartbeat reports, names `ReportPublisherFactory`, `ReportManager`, and `ReportPublisher`, describes how to add a new report, and includes a sequence diagram for construction, initialization, periodic publishing, heartbeat transfer, and shutdown.

State and persistence: none.

Dependencies and integration: documents the integration between `DatanodeStateMachine`, `ReportManager`, `ReportPublisher`, and SCM heartbeat RPC.

Risks and test signals: no runtime tests. Documentation should be updated when new report types are added, the scheduling model changes, or report flow differs from the sequence diagram.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/package-info.java -->
