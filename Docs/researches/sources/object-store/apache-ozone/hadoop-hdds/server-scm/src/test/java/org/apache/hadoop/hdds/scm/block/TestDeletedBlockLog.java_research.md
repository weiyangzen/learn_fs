# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestDeletedBlockLog.java

## Purpose

This large test class exercises `DeletedBlockLogImpl` and `SCMDeletedBlockTransactionStatusManager`, the SCM-side transaction log used to send deleted-block transactions to datanodes and remove them after enough acknowledgements. It validates batching, persistence, per-datanode command status, resend suppression, timeout behavior, unhealthy-container filtering, and data-distribution summaries.

## Important APIs, Types, and Functions

- `DeletedBlockLogImpl.addTransactions`, `getTransactions`, `recordTransactionCreated`, `onSent`, and `close` are central APIs.
- `SCMDeletedBlockTransactionStatusManager.commitTransactions`, `commitSCMCommandStatus`, `getTransactionSummary`, `removeTransactions`, and `getTxSizeMap` are exercised directly or indirectly.
- Helper methods `generateData`, `updateContainerMetadata`, `commitTransactions`, `getTransactions`, `recordScmCommandToStatusManager`, and `sendSCMDeleteBlocksCommand` model the SCM-to-DN lifecycle.
- `mockStandAloneContainerInfo`, `mockInadequateReplicaUnhealthyContainerInfo`, and `mockContainerHealthResult` shape replication health and replica placement.

## Control Flow and State Behavior

`setup` creates a temporary SCM, mocks `ReplicationManager` and `ContainerManager`, opens the SCM container table, installs an HA transaction buffer stub, creates delete-service metrics, and constructs `DeletedBlockLogImpl`. Generated test transactions create one container per transaction and five deleted blocks per container. `getTransactions` asks the log for work for selected DNs, then records each created `DeleteBlocksCommand` in the status manager and marks it sent.

The tests prove that unflushed transactions are invisible, flushing advances container delete transaction IDs, and iterator progress avoids resending in-flight transactions. Commit tests show that invalid transaction IDs are ignored, partial DN acknowledgements leave transactions pending, and command timeout enables resend. Command-status tests cover unsent, sent, pending, failed, and timed-out commands. Replica-health tests prevent deletion commands when a container is unhealthy or has inadequate replicas. Standalone containers route transactions to their single hosting DN. Parameterized tests assert max-blocks-per-datanode splitting and optional data-distribution summary behavior.

## State and Persistence

The class uses real SCM metadata tables for containers and deleted block transactions, plus `SCMHADBTransactionBufferStub` to control flush boundaries. It explicitly closes and reopens `DeletedBlockLogImpl` to verify persisted transactions and current transaction state. It also mutates in-memory `containers` and `replicas` maps that back mocked `ContainerManager` calls.

## Dependencies and Integration Points

Dependencies include SCM metadata tables, HA transaction buffering, `ContainerManager`, `ReplicationManager`, `ContainerHealthResult`, `DeleteBlocksCommand`, datanode command status protos, `ScmBlockDeletingServiceMetrics`, and Ozone `DeletedBlock`/`BlockID`. The file ties block deletion to container health, container delete transaction IDs, datanode command reporting, and DB persistence.

## Risks and Test Signals

High-risk behavior includes duplicate delete transaction delivery, premature DB removal before enough DN acknowledgements, lost command-status state, slow large-batch operations, and deleting blocks from unhealthy or already deleted containers. The strongest signals are DB reopen persistence checks, timeout/resend assertions, no-duplicate set comparisons, and randomized add/get/commit/invariant loops.
