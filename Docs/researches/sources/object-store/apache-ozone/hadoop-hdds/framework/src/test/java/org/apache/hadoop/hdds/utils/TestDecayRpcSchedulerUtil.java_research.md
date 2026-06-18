<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestDecayRpcSchedulerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestDecayRpcSchedulerUtil.java

Purpose: tests helpers for parsing DecayRpcScheduler metrics and creating username metric tags.

Important APIs/types/functions: `DecayRpcSchedulerUtil.splitMetricNameIfNeeded`, `checkMetricNameForUsername`, `createUsernameTag`, and Hadoop `MetricsTag`.

Control flow: tests split a DecayRpcScheduler metric name containing username and metric type, verify unrelated metrics remain unchanged, extract username from scheduler metric names, return null for unrelated metrics, and create optional username tags only when username is non-null.

State and persistence behavior: pure string/tag processing with no external state.

Dependencies and integration points: supports metrics formatting and tagging for scheduler/user-level Prometheus or Metrics2 output.

Risks: metric-name parsing depends on exact record and metric naming conventions; changes upstream in scheduler metric names can break extraction.

Test signals: asserts split metric type, unchanged random metrics, username extraction, null extraction for unrelated metrics, absent tag for null username, and tag name/value/description for non-null username.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestDecayRpcSchedulerUtil.java -->
