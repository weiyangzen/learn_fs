# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestClosePipelinesSubCommand.java

Purpose: This parameterized test validates `ClosePipelineSubcommand --all` filtering before issuing close operations.

Important APIs and types: It builds `Pipeline` instances with `StandaloneReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, `PipelineID`, and synthetic `DatanodeDetails`, then mocks `ScmClient.listPipelines`.

Control flow: A method source supplies CLI flags and expected "Sending close command" counts. Setup creates the command, captures streams, and returns a mixed pipeline list. Each case parses flags, executes the command, and asserts exact stdout.

State and persistence behavior: No durable state is touched. Runtime state is a generated pipeline list with OPEN and CLOSED states.

Dependencies and integration points: The suite anchors close-all filter semantics across replication factor, replication type, EC config strings, and legacy factor flags.

Risks: The test verifies only the printed count, not that the expected pipeline IDs are closed or that `ScmClient.closePipeline` is called. Random IDs are irrelevant to assertions.

Test signals: Exact output counts for unfiltered, RATIS factor, EC replication/type, type-only, and closed-only cases.
