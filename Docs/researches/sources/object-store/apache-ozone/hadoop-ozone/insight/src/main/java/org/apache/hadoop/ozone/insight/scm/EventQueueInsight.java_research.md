<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/EventQueueInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/EventQueueInsight.java

Purpose: insight point for SCM internal asynchronous event delivery.

Important APIs: `getRelatedLoggers` returns the SCM `EventQueue` logger at default TRACE/DEBUG level. `getDescription` describes internal async event delivery. It inherits empty metrics and config classes.

Control flow and integration: used by `ozone insight log scm.event-queue` to stream SCM event queue logs.

State and persistence: stateless. No persistence.

Risks and tests: no metric or config support. Logging volume can be high at TRACE. No direct tests cover this insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/scm/EventQueueInsight.java -->
