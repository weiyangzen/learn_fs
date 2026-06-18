<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ListSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ListSubCommand.java

Purpose: picocli `list` subcommand that prints available insight point names and descriptions, optionally filtered by prefix.

Important APIs: optional parameter `insightPrefix`, `call()` creates insight points with a fresh `OzoneConfiguration`, iterates the linked map, and prints names formatted to 33 characters beside descriptions.

Control flow and integration: relies on `BaseInsightSubCommand.createInsightPoints` preserving deterministic insertion order. It does not need a live cluster except to instantiate datanode insight objects with a configuration.

State and persistence: no persistent state.

Risks and tests: output is written directly to stdout and has no direct unit test. Prefix filtering is simple `startsWith`; empty default lists all. Future insight points requiring expensive construction would affect list latency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/ListSubCommand.java -->
