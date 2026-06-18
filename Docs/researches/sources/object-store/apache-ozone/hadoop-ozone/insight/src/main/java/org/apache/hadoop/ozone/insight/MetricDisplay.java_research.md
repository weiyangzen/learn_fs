<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricDisplay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricDisplay.java

Purpose: descriptor for one Prometheus metric value to display in the Insight CLI.

Important APIs: constructors accept description, metric id, and optional tag filter map. Getters expose id, description, and filter. `checkLine(String)` currently returns false and is unused by `MetricsSubCommand`.

Control flow and integration: insight implementations build these descriptors; `MetricsSubCommand.selectValue` independently matches prometheus lines by `id` and tag filters, then returns the second whitespace-separated token as the value.

State and persistence: local immutable-ish descriptor; filter map reference is mutable if shared externally. No persistence.

Risks and tests: `checkLine` is a stub, which can mislead maintainers. Filter maps are not defensively copied. Metric names and tag names are hardcoded in callers. No direct test covers metric selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricDisplay.java -->
