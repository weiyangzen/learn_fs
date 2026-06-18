<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDiskBalancerSubCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDiskBalancerSubCommands.java

Purpose: Comprehensive unit tests for datanode disk balancer CLI start, stop, update, status, and report commands across single node, multiple nodes, stdin, batch in-service datanodes, JSON output, and failure cases.

Important APIs and types: `DiskBalancerStartSubCommand`, `DiskBalancerStopSubCommand`, `DiskBalancerUpdateSubCommand`, status/report commands, `DiskBalancerSubCommandUtil`, static Mockito mocks, `ReconfigureProtocol`, `DiskBalancerConfigurationProto`, `DatanodeDiskBalancerInfoProto`, volume info protos, Picocli, and captured stdout/stderr.

Control flow: A `DiskBalancerMocks` helper mocks SCM datanode discovery, single-node reconfigure proxies, and all-operable-node lookup. Tests parse command options, execute commands, and assert result text or JSON. Start/update build configuration from threshold, bandwidth, parallelism, and disk balancing flag; stop calls the stop RPC; status/report read generated/random status protos; failures throw or print per-node errors depending on command path.

State and persistence behavior: No real datanode state. Mock protocol responses model disk balancer runtime state, volume density, ideal usage, capacities, utilization, and configuration. Static mocks are closed via AutoCloseable to avoid leakage.

Dependencies and integration points: Exercises CLI integration with datanode reconfigure protocol and SCM node discovery, including batch operations over in-service datanodes and JSON serialization of command results.

Risks: Heavy static mocking can leak if not closed. Randomized report/status protos increase coverage but can make debugging output variable. Tests assert key JSON fields rather than full schemas. Some failure paths report text rather than exception behavior.

Test signals: Start/update/stop success for batch and explicit hosts, duplicate host handling, stdin host parsing, JSON fields for action/status/configuration/report volumes, invalid container-state update error, status/report for multiple nodes, and connection/stop/update/report failure messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDiskBalancerSubCommands.java -->
