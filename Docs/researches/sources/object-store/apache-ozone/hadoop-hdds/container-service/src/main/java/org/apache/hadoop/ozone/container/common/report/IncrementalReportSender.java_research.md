<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/IncrementalReportSender.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/IncrementalReportSender.java

Purpose: generic interface for publishing incremental container reports.

Important APIs and control flow: `send` publishes immediately and may trigger heartbeat. `sendDeferred` defaults to `send`, but implementations can override it to queue the report until the next scheduled heartbeat.

State and persistence: interface only. Implementations likely mutate `StateContext` pending ICR queues.

Dependencies and integration: used by `Handler` to notify SCM of container state changes or defer reports when no state change occurred.

Risks and test signals: implementations should test immediate heartbeat triggering, deferred queue behavior, deduplication, exception handling, and behavior for recovering containers as filtered by `Handler`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/report/IncrementalReportSender.java -->
