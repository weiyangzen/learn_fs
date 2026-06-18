<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStatusSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStatusSubcommand.java

Purpose: Prints the current or last reconfiguration task status for selected nodes, including per-property success and failure details after completion.

Important APIs and types: `ReconfigureProtocol.getReconfigureStatus()`, `ReconfigurationTaskStatus`, `ReconfigurationUtil.PropertyChange`, `Optional<String>` error values, `Date`, and inherited target dispatch.

Control flow: `executeCommand` opens a proxy, reads server name and task status, prints a node prefix, and delegates to `printReconfigurationStatus`. Status printing handles no task, running task, stopped task with no property status, and stopped task with per-property results. Success is represented by absent error optional; failure prints the error text.

State and persistence behavior: Read-only from the CLI side. It observes server-side reconfiguration task timestamps and result maps.

Dependencies and integration points: Uses Hadoop common reconfiguration status types and the Ozone reconfigure protocol translator.

Risks: IOExceptions are printed with stack traces but not rethrown, similar to start. Date formatting uses default JVM timezone/locale. Output is plain text and may be parsed by scripts.

Test signals: No-task, running, completed success/failure map, null status map, IOException handling, and batch output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStatusSubcommand.java -->
