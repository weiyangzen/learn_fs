<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestLogSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestLogSubcommand.java

Purpose: unit test for `LogSubcommand.processLogLine`.

Important APIs: constructs a log line containing a `<json>...</json>` payload with escaped newlines, calls `processLogLine`, and asserts the result splits into 10 newline-separated lines.

Control flow and test signals: verifies embedded structured payloads are expanded for readability when streamed by the log command.

State and persistence: none.

Dependencies and integration: JUnit 5 only.

Risks and gaps: test method name `filterLog` is misleading. It does not assert exact formatted output, multiple JSON regions, malformed tags, HTTP streaming, log level changes, or shutdown restoration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/test/java/org/apache/hadoop/ozone/insight/TestLogSubcommand.java -->
