# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestDeletedBlocksTxnShell.java

## Purpose
`TestDeletedBlocksTxnShell` verifies the SCM admin subcommand that reports deleted block transaction summary totals.

## Important APIs, Types, and Functions
The test starts a 3-SCM HA mini cluster with one OM, gets the SCM leader, creates synthetic `DeletedBlock` entries, adds them to `DeletedBlockLog`, flushes the leader SCM HA DB transaction buffer, and runs `GetDeletedBlockSummarySubcommand.execute` through a `ContainerOperationClient`. It also seeds `ContainerStateManager` with `ContainerInfo` and three closed `ContainerReplica` entries per container.

## Control Flow, State, and Persistence
`generateData(30)` creates 30 container transaction groups, each containing five deleted blocks of fixed logical and replicated sizes. `updateContainerMetadata` adds closed container metadata and replicas to SCM so the deleted block log can accept transactions. The test flushes SCM leader DB state, asserts summary counts from `DeletedBlockLog.getTransactionSummary`, executes the CLI subcommand, and checks stdout contains the same totals. Persistent state is SCM deleted block log and container metadata in the HA SCM DB.

## Dependencies and Integration Points
This integrates SCM HA, deleted block log, container state manager, container replicas, SCM transaction buffer flushing, admin shell command execution, and stdout capture.

## Risks and Test Signals
Risks include assuming the first leader-ready SCM stream entry is stable and needing manual flush to avoid uncommitted state. Signals are exact totals for transactions, block count, logical size, replicated size, and matching command output.
