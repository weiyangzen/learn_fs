# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/DeleteBlocksCommandHandler.java

## Purpose
`DeleteBlocksCommandHandler` processes SCM delete-block commands by marking block metadata for asynchronous deletion and updating delete-block command status ACKs back to SCM.

## Important APIs and Types
Implements `CommandHandler` for `deleteBlocksCommand`. It owns a bounded `LinkedBlockingQueue<DeleteCmdInfo>`, a daemon `DeleteCmdWorker`, a fixed transaction executor, `ProcessTransactionTask`, `DeleteBlockTransactionExecutionResult`, schema-specific `SchemaHandler`s, and `BlockDeletingServiceMetrics`. Test-visible APIs include `executeCmdWithRetry()`, `submitTasks()`, `getSchemaHandlers()`, `getBlockDeleteMetrics()`, and `setPoolSize()`.

## Control Flow
`handle()` enqueues a delete command; if the queue is full, it marks the command failed with an empty ACK. The worker drains queued commands and calls `processCmd()`. Processing summarizes transactions, records metrics, submits per-transaction tasks, retries lock-acquisition failures once, builds a `ContainerBlocksDeletionACKProto`, and updates the `DeleteBlockCommandStatus` as executed or failed.

## State and Persistence Behavior
For key-value containers, each transaction tries to acquire the container write lock with a configured timeout. It rechecks `ContainerSet` after locking to avoid acting on stale container objects after DiskBalancer moves. Schema v1 moves block entries to deleting keys and deletes unreferenced files; schemas v2 and v3 write delete-transaction tables using different key types. Metadata updates include latest delete transaction ID, pending delete block count, and optionally pending delete bytes after layout-feature finalization.

## Dependencies and Integration Points
It integrates with `ContainerSet`, `KeyValueContainerData`, `BlockUtils`, `DeleteTransactionStore`, RocksDB batch operations, `VersionedDatanodeFeatures`, command status reports, block deletion metrics, and `OzoneContainer` dispatchers.

## Risks
This is concurrency and persistence sensitive. Lock timeouts lead to one retry, then failed transaction ACKs. Duplicate and out-of-order transaction logic is based on in-memory container delete transaction ID. Schema-specific table keys must match container DB layout. Queue overflow fails the command immediately. Errors in `processCmd()` still run the status updater in `finally`, but an ACK may be null on failure.

## Test Signals
Tests should cover queue overflow status, schema v1/v2/v3 marking, duplicate and out-of-order transactions, lock timeout retry, stale container after DiskBalancer move, metadata counter updates, pending-byte feature gating, command ACK contents, worker shutdown, and executor resizing.
