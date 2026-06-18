<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionStatusSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionStatusSubCommand.java

Purpose: Tests datanode decommission status output for all nodes and filtered node selection by ID or IP, including success/failure health, metrics, container lists, no-node output, and unsupported hostname filtering.

Important APIs and types: `DecommissionStatusSubCommand`, mocked `ScmClient`, `HddsProtos.Node`, `DatanodeDetails`, `ContainerID`, SCM metrics strings, Picocli, parameterized `--id`/`--node-id`, and captured output streams.

Control flow: Fixtures create two decommissioning node protos, per-node container lists, and metrics strings. Tests mock `queryNode`, `getContainersOnDecomNode`, and `getMetrics`, parse filter options, execute the command, and assert which hostnames, metrics, and container IDs appear. Hostname option test expects a `ParameterException`.

State and persistence behavior: No persistence. Mocked SCM state represents node operational state, pending containers, and decommission metrics.

Dependencies and integration points: Validates the CLI's use of SCM node query and decommission progress APIs and the supported filter contract.

Risks: Metrics are opaque strings from SCM and are asserted by substring. The command rejects hostname filtering despite common operator expectations; the test locks this behavior.

Test signals: Both nodes shown by default, no-node message with no metrics/container lists, ID and IP filters include only matching host, success/failure metrics alter container display, and `--hostname` is rejected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionStatusSubCommand.java -->
