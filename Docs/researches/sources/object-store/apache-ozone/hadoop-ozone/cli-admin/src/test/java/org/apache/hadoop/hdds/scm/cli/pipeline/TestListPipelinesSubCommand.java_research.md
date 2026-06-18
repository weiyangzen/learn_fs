# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestListPipelinesSubCommand.java

Purpose: This test suite verifies `ListPipelinesSubcommand` filtering by pipeline state, replication type, replication config, and legacy factor/state flags.

Important APIs and types: It uses Ozone replication config classes, `Pipeline`, `PipelineID`, `DatanodeDetails`, mocked `ScmClient.listPipelines`, and picocli parsing.

Control flow: Setup builds six pipelines across STANDALONE, RATIS, and EC replication with OPEN/CLOSED states. Each test parses specific options, executes the command, and checks output line counts or absence of unrelated state/type strings.

State and persistence behavior: No persistence is involved. Runtime state is generated pipeline metadata and captured stdout.

Dependencies and integration points: The test protects filter compatibility between modern `-r/-t/-s` flags and legacy `-ffc/-fst` flags.

Risks: Assertions mostly count lines and search substrings, so they can miss subtle formatting or wrong-ID issues. Exceptions are asserted at execute time rather than parse time for invalid combinations.

Test signals: All pipelines returned with no filter, OPEN-only exclusion of CLOSED, illegal replication without type, mutual exclusion of legacy and modern replication filters, EC config matching, and combined state/replication filters.
