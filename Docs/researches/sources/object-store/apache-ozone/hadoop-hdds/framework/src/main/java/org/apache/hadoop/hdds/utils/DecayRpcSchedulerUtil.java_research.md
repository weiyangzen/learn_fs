# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DecayRpcSchedulerUtil.java

Purpose: `DecayRpcSchedulerUtil` normalizes DecayRpcScheduler metrics for Prometheus by extracting caller usernames from metric names and converting them to labels.

Important APIs/types/functions: `splitMetricNameIfNeeded(recordName, metricName)` returns `Volume` or `Priority` for DecayRpcScheduler caller metrics, otherwise the original metric name. `checkMetricNameForUsername()` extracts the username inside `Caller(...)` for matching metrics. `createUsernameTag()` returns an optional Metrics2 tag named `username`.

Control flow: Prometheus metrics normalization calls these helpers when building metric names/tags. Matching is based on lowercase contains checks for `decayrpcscheduler` and `caller(`, then string splitting by `.` and parentheses.

State and persistence: stateless utility class.

Dependencies/integration: used by `PrometheusMetricsSinkUtil` and metrics export code. Depends on Guava `Strings`, Metrics2 `MetricsInfo`/`MetricsTag`, and Java `Optional`.

Risks: parsing assumes exactly the expected `Caller(user).Metric` shape; malformed matching strings can cause array index exceptions. Usernames containing `.` or parentheses would break parsing assumptions.

Test signals: `TestDecayRpcSchedulerUtil` covers metric-name splitting, unchanged names, username extraction, null username behavior, and username tag creation.
