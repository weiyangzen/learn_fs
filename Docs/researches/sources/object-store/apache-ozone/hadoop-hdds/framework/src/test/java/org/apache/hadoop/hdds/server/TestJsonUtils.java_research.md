<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestJsonUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestJsonUtils.java

Purpose: verifies JSON pretty-printing for representative HDDS client objects, specifically `OzoneQuota` instances.

Important APIs/types/functions: `JsonTestUtils.toJsonStringWithDefaultPrettyPrinter`, `OzoneQuota.getOzoneQuota`, `OzoneQuota.getOzoneQuotaNameSpace`, and the local `assertContains` helper.

Control flow: creates a space quota and a namespace quota, serializes each with the default pretty printer, and asserts selected fields are present in the JSON string.

State and persistence behavior: no external state. Objects are constructed in memory and converted to strings.

Dependencies and integration points: integrates client-side quota model classes with the repository JSON utility layer and AssertJ string assertions.

Risks: tests only selected substrings, so formatting and additional fields can change without failure. It is useful for detecting field-name or serialization-regression changes for quota output.

Test signals: asserts `rawSize`, `unit`, and `quotaInNamespace` fields appear with expected values in pretty-printed JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/TestJsonUtils.java -->
