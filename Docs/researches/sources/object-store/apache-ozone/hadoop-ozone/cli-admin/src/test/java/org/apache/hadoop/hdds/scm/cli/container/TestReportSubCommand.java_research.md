<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReportSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReportSubCommand.java

Purpose: Tests the container replication manager report CLI for empty reports, JSON output, and populated unhealthy-container samples.

Important APIs and types: `ReportSubcommand`, mocked `ScmClient`, `ReplicationManagerReport`, `ContainerHealthResult.HealthState`, `ContainerID`, `ContainerInfo`, Picocli, regex matchers, and captured stdout/stderr.

Control flow: Tests mock `getReplicationManagerReport()` to return either an empty report or a report populated by `createReport()`. The command is executed with default or `--json` args, and output is matched for report timestamp, health counters, missing/under/over/unhealthy states, and limited container ID lists.

State and persistence behavior: No real persistence. The report object holds in-memory counts and sample unhealthy containers that model SCM replication-manager state.

Dependencies and integration points: Validates CLI formatting for SCM replication manager reports and the JSON branch consumed by operators or tools.

Risks: Regex assertions are formatting-sensitive but do not fully validate JSON semantics. The fixture samples a bounded container list, so truncation behavior is represented by helper-generated ranges.

Test signals: Empty report shows zero counts for all health states, valid JSON begins with expected report fields, populated report shows expected counts and sample container lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReportSubCommand.java -->
