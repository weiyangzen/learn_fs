# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestDeleteBlocksCommandHandler.java

## Purpose
`TestDeleteBlocksCommandHandler` validates delete-block command execution, schema-handler dispatch, retry behavior, lock timeout handling, queue saturation status, duplicate transaction accounting, and stale container-data retry behavior.

## Important APIs, Types, And Functions
- `DeleteBlocksCommandHandler.executeCmdWithRetry`, `submitTasks`, `handle`, `stop`, `getSchemaHandlers`, and nested `DeleteCmdWorker` are tested.
- `SchemaHandler.handle` is replaced with test handlers for schema V1, V2, and V3.
- `DeleteBlocksCommand`, `DeletedBlocksTransaction`, `DeleteBlockTransactionResult`, and `CommandStatus` model SCM delete-block work and acknowledgements.
- `KeyValueContainerData.incrPendingDeletionBlocks`, `updateDeleteTransactionId`, and duplicate detection update container deletion state.
- `DatanodeConfiguration` block delete queue limit and worker interval are exercised.

## Control Flow
Setup creates a mocked `OzoneContainer`, a `ContainerSet` with closed key-value containers attached to a mocked volume, a spy `DeleteBlocksCommandHandler`, and schema handler spies keyed by schema version. Basic execution builds a transaction for an existing container and asserts the matching schema handler runs once and returns success. Timeout tests manually hold a container write lock: one case leaves it locked so that transaction fails after retry while another transaction succeeds; another releases the lock after the first submit so retry succeeds. Exception handling stubs `submitTasks` to include a failed future followed by success and asserts execution continues. Queue-full handling sets a small delete queue limit, sends more commands than capacity, and expects early statuses `PENDING` then later statuses `FAILED` with empty block deletion ACKs. Duplicate transaction tests execute identical and older transaction IDs to ensure success is idempotent and pending deletion counters are not double-counted for the same transaction content. The stale-container test spies `ContainerSet.getContainer` to return an old replica, then a new replica, proving the first stale attempt skips schema handling and retry handles the live replica.

## State And Persistence Behavior
The suite exercises in-memory container deletion state that would later drive block deletion persistence: pending deletion block count, pending deletion bytes, and last delete transaction ID. It also checks container write locks, command status map behavior through `StateContext`, and queue capacity. No actual block files are deleted; schema handlers simulate metadata mutation.

## Dependencies And Integration Points
Dependencies include `ContainerTestVersionInfo` schema parameterization, `ContainerLayoutVersion`, `BlockDeletingServiceMetrics`, `StateContext`, `DatanodeStateMachine`, `SCMConnectionManager`, `HddsVolume`, and protobuf delete transaction/result types. The test protects integration between SCM delete-block commands, container locking, schema-specific DB mutation, metrics, and heartbeat command-status reporting.

## Risks And Edge Cases
Critical covered risks include lock leaks/timeouts, retry not happening, failure of one future aborting all results, queue saturation not reporting failure, duplicate SCM transactions inflating deletion counters, older transactions being incorrectly skipped, and DiskBalancer-style container map swaps causing stale metadata mutation.

## Test Signals
Signals include schema-handler invocation counts, submit retry counts, result success flags by transaction ID, block-delete metrics, command status values, ACK result counts, pending block/byte counters, and stale-replica handler exclusion.
