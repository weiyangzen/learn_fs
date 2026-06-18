<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportManager.java

Purpose: lifecycle manager for configured report publishers and their shared scheduled executor.

Important APIs and control flow: private construction stores `StateContext`, publisher list, and creates a daemon scheduled thread pool sized to the publisher count with optional thread name prefix. `init` initializes each publisher with the context and executor. `shutdown` shuts down the executor and waits up to five seconds, restoring interrupt status if interrupted. The builder owns a `ReportPublisherFactory`, accumulates publisher instances or report classes, records state context and thread prefix, and validates context during `build`.

State and persistence: owns executor service and publisher list. No disk persistence; it changes report scheduling state.

Dependencies and integration: used by datanode state machine startup to wire node, container, command status, and pipeline publishers.

Risks and test signals: tests should cover zero publishers, executor thread naming, shutdown interrupt handling, missing state context validation, factory publisher addition, direct publisher addition, and repeated init/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/ReportManager.java -->
