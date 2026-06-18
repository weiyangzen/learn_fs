<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisNameRewrite.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisNameRewrite.java

Purpose: parameterized tests for Ratis metric-name normalization and label extraction.

Important APIs/types/functions: `RatisNameRewriteSampleBuilder.normalizeRatisMetric`, parameterized `Arguments`, mutable tag name/value lists, and expected normalized metric names.

Control flow: `parameters()` supplies original Ratis metric names plus expected Prometheus names and tag arrays. The test calls the normalizer, then compares the normalized name and populated tag lists to expectations.

State and persistence behavior: no persistent state. The method mutates supplied `List<String>` instances to append tag names and values.

Dependencies and integration points: integrates Ozone Prometheus naming conventions with Ratis metric naming schemes for groups, peers, instances, and subcomponents.

Risks: normalization logic is compatibility-sensitive for dashboards and alerting. Parameter expectations must track both Ratis name changes and Prometheus label rules.

Test signals: asserts exact normalized names and exact ordered tag names/values for each representative Ratis metric pattern.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestRatisNameRewrite.java -->
