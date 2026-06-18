# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestUsageInfoSubcommand.java

Purpose: This suite verifies the standalone datanode usage report command in JSON and text modes.

Important APIs and types: It uses `UsageInfoSubcommand`, mocked `ScmClient.getDatanodeUsageInfo`, protobuf `DatanodeUsageInfoProto`, `MockDatanodeDetails`, Jackson `JsonNode`, AssertJ text assertions, and picocli.

Control flow: The fixture redirects output, stubs one usage record, parses `-m` with or without `--json`, executes the command, then checks JSON numeric fields or text labels.

State and persistence behavior: There is no persistence. The command consumes in-memory protobuf usage data and emits formatted report output.

Dependencies and integration points: The test protects the CLI mapping from SCM usage protobuf fields to operator-visible values: Ozone capacity, used, available, filesystem values, container count, and pipeline count.

Risks: Percentage calculations are validated for one simple fixture only. Text alignment assertions depend on label spacing and may require updates after formatting changes.

Test signals: JSON array node type, datanode details presence, exact capacity/usage values and percentages, and presence of every expected aligned text field.
