<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricGroupDisplay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricGroupDisplay.java

Purpose: groups related `MetricDisplay` entries under a component and human-readable section title.

Important APIs: constructors accept a `Component` or component `Type` plus description. `addMetrics` appends descriptors. Getters expose metrics, description, and component.

Control flow and integration: insight implementations return lists of groups. `MetricsSubCommand` collects unique components from groups, fetches each component's `/prom` endpoint once, then prints groups in the supplied order.

State and persistence: mutable list of metrics; no persistence.

Risks and tests: no defensive copy on `getMetrics`; callers can mutate the list. Component equality affects endpoint de-duplication. No direct tests cover grouping behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/MetricGroupDisplay.java -->
