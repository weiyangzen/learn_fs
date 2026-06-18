<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisher.java

Purpose: abstract scheduled report publisher base class.

Important APIs and control flow: `init` stores context/executor and schedules `run` at a fixed rate using `getReportFrequency` for both initial delay and period. `run` skips publishing when executor is shut down or datanode state is SHUTDOWN. `publishReport` calls subclass `getReport`; command status reports are added as incremental reports, while all other reports refresh full report state. IO exceptions are logged. Subclasses provide frequency and report generation.

State and persistence: holds config, context, and executor references. It mutates `StateContext` report queues/full report slots.

Dependencies and integration: base for node, container, command status, and pipeline publishers. Depends on protobuf `Message`, `StateContext`, and datanode state enum.

Risks and test signals: `getReport` may return null; tests should verify `StateContext` handling or whether null reports should be skipped by future changes. Frequency is evaluated twice during init, which can produce different random delays for publishers that add jitter. Shutdown-state skipping and IO logging should be tested.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportPublisher.java -->
