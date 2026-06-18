# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestListInfoSubcommand.java

Purpose: This JUnit suite verifies the SCM admin datanode `ListInfoSubcommand` output contract for text and JSON modes. It exercises listing all nodes, selecting a node by UUID, ordering by usage, volume counters, and filtering nodes that have failed volumes.

Important APIs and types: The test constructs protobuf `HddsProtos.Node` and `DatanodeUsageInfoProto` values, mocks `ScmClient.queryNode`, `ScmClient.getDatanodeUsageInfo`, and `ScmClient.listPipelines`, drives parsing with picocli `CommandLine`, and validates JSON through Jackson `ObjectMapper`.

Control flow: Each test configures a mock SCM response, parses CLI arguments into the same command instance, invokes `cmd.execute(scmClient)`, and inspects captured stdout/stderr. Helper methods build four nodes with varied health and operational states and validate JSON/text usage ordering.

State and persistence behavior: There is no persistent state. Runtime state is captured console output, mutable command options parsed by picocli, and generated UUID-backed protobuf fixtures.

Dependencies and integration points: The test anchors the CLI-to-`ScmClient` boundary and output fields consumed by operators and automation, including `--json`, `--id`, `--most-used`, `--least-used`, and `--nodes-with-failed-volumes`.

Risks: Several assertions depend on exact labels and ordering, so formatting changes can break tests even when data is correct. Reusing the command instance after parsing different flags relies on command option reset behavior.

Test signals: Signals include valid JSON arrays, expected node counts, presence and ordering of health states, mutual-exclusion exceptions, usage ratio sorting, volume count fields, failed volume paths, and rejection of failed-volume filtering with explicit node selection.
