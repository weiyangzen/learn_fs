<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestInfoSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestInfoSubCommand.java

Purpose: Tests container info CLI parsing and output for single/multiple container IDs, stdin input, JSON output, replica inclusion, EC replica indexes, and replica-fetch errors.

Important APIs and types: `InfoSubcommand`, mocked `ScmClient`, `ContainerWithPipeline`, `ContainerInfo`, `Pipeline`, `ContainerReplicaInfo`, `ECReplicationConfig`, `RatisReplicationConfig`, `PipelineNotFoundException`, Picocli, Jackson `JsonNode`, and captured output streams.

Control flow: Setup mocks `getContainerWithPipeline` by ID and makes missing pipeline lookup throw. Tests parse args or feed stdin, run `cmd.execute(scmClient)`, then validate human or JSON output. Helpers construct containers, datanode UUIDs, replica sets with optional replica indexes, and validate invalid ID failures.

State and persistence behavior: No persistence; all SCM state is mocked. Runtime state includes captured standard streams and generated datanode/container fixtures.

Dependencies and integration points: Exercises CLI behavior over SCM container info, pipeline and replica retrieval, stdin parsing convention using `-`, and JSON schema emitted by the command.

Risks: Regex-based validation is sensitive to formatting. Replica-fetch errors are expected to omit replicas rather than fail the whole command, which is a behavior contract. Pipeline-not-found is mocked globally and may not cover pipeline-success rendering.

Test signals: Missing parameter exception, invalid ID `ParameterException`, multiple container outputs, stdin and JSON stdin handling, UUID patterns in replica output, sorted replica indexes for EC, absence of replicas on errors, and JSON containing/omitting `replicas` as expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestInfoSubCommand.java -->
