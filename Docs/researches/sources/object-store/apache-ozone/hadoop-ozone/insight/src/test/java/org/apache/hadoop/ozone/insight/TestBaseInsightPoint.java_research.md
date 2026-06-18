<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightPoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightPoint.java

Purpose: unit test for common `BaseInsightPoint.filterLog` behavior.

Important APIs: creates an anonymous `BaseInsightPoint` with a dummy description and asserts filter matching for one datanode filter, empty filters, and combined datanode plus pipeline filters.

Control flow and test signals: verifies that all configured filters must be present as bracketed `[key=value]` tokens in a log line and that an empty map permits all lines. It also verifies mismatched values reject lines.

State and persistence: no external state or persistence.

Dependencies and integration: JUnit 5 assertions and Java maps only.

Risks and gaps: does not cover `filters == null`, regex metacharacters in filter values, or log lines containing multiple bracketed values. It also does not cover other BaseInsightPoint helpers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestBaseInsightPoint.java -->
