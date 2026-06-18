# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerStateMachine.java

## Purpose
`OzoneManagerStateMachine` is the Ratis state machine that applies committed OM log entries to the `OzoneManager`. It validates transactions, serializes write application, feeds responses into the double buffer, serves read queries, tracks snapshots, and handles leader/snapshot lifecycle callbacks.

## Important APIs and Types
- Constructor loads snapshot info from OM DB, builds `OzoneManagerDoubleBuffer`, creates an `OzoneManagerRequestHandler`, and starts single-thread executors for apply and snapshot install.
- Ratis hooks include `initialize`, `reinitialize`, `getLatestSnapshot`, `notifyLeaderReady`, `notifyNotLeader`, `notifyLeaderChanged`, `notifyTermIndexUpdated`, `notifyConfigurationChanged`, `notifySnapshotInstalled`, `startTransaction`, `preAppendTransaction`, `applyTransaction`, `query`, `pause`, `takeSnapshot`, `notifyInstallSnapshotFromLeader`, and `close`.
- `runCommand`, `createErrorResponse`, and `processResponse` are the main write-execution helpers.

## Control Flow
`startTransaction` decodes an `OMRequest`, validates group id and request shape, and either returns a context with exception or one containing log data and the decoded request. `preAppendTransaction` handles prepare-mode authorization and gating before the log append. `applyTransaction` decodes the request from context or log data, builds a `TermIndex`, acquires one double-buffer backpressure permit, then schedules `runCommand` on a single-thread executor. This serialization preserves deterministic application order across OM replicas.

`runCommand` builds an `ExecutionContext`, delegates write handling to `RequestHandler.handleWriteRequest`, obtains lock details from the response, and returns the `OMResponse` possibly augmented with protobuf lock timing. On `IOException`, it creates a failed response and still adds a `DummyOMClientResponse` to the double buffer so transaction index advancement remains consistent. `processResponse` terminates OM for critical `INTERNAL_ERROR` and `METADATA_ERROR`, but converts successful and non-critical responses to Ratis messages.

Read-only `query` decodes an OM request and delegates to `handler.handleReadRequest` without appending a log entry. Snapshot methods use `TransactionInfo` stored in OM DB as the Ratis snapshot marker. `takeSnapshot` waits for skipped term-index notifications to be covered by double-buffer flushes, writes `TRANSACTION_INFO_KEY`, flushes RocksDB, and returns the snapshot index. Snapshot installation is delegated asynchronously to `ozoneManager.installSnapshotFromLeader`.

## State and Persistence Behavior
The state machine persists last-applied term/index through `TransactionInfo` in OM DB and relies on `OzoneManagerDoubleBuffer` for actual metadata writes. It tracks in-memory `lastNotifiedTermIndex`, `lastSkippedIndex`, `previousLeaderId`, pause count, executors, double buffer, handler, and Netty metrics. On restart/reinitialize it reloads transaction info from DB.

## Dependencies and Integration Points
It integrates with Apache Ratis `BaseStateMachine`, `OzoneManager`, `OzoneManagerRequestHandler`, `OzoneManagerDoubleBuffer`, `OzoneManagerPrepareState`, OM metrics/audit, `OMRatisHelper`, `ExecutionContext`, and snapshot provider installation. `OzoneManagerRatisServer` owns it.

## Risks and Edge Cases
The single apply executor is intentionally conservative but can bottleneck throughput. A semaphore permit is acquired before async execution; if a path fails before double-buffer add/release, writes can stall. The prepare gate must reject non-prepare/cancel writes consistently on all nodes. Critical error termination is required to prevent DB divergence. Snapshot logic relies on transaction info monotonicity and correct handling of Ratis term-index notifications for non-state-machine log entries.

## Test Signals
Tests should cover request validation failures, prepare authorization and gating, serialized apply order, backpressure, error response index advancement, critical error termination, read query bypass, snapshot transaction info loading/writing, pause/unpause double-buffer rebuild, leader change notifications, configuration change peer updates, and install-snapshot async error propagation.
