<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/CommandStatusReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/CommandStatusReportHandler.java

## Purpose
Handles datanode command status reports on the SCM event bus and routes delete-block command status entries to the block deletion status pipeline.

## Important APIs, Types, And Functions
`CommandStatusReportHandler` implements `EventHandler<CommandStatusReportFromDatanode>`. `onMessage` validates the report and command list, filters `CommandStatus` entries by `SCMCommandProto.Type.deleteBlocksCommand`, and fires `SCMEvents.DELETE_BLOCK_STATUS` with a `DeleteBlockStatus` payload. Nested `CommandStatusEvent` implements `IdentifiableEventPayload` and wraps a list of statuses with an ID from `HddsIdFactory.getLongId()`. `DeleteBlockStatus` adds the reporting `DatanodeDetails`.

## Control Flow
On each report, the handler logs trace details, scans the command statuses, ignores unsupported command types with debug logging, batches all delete-block statuses from the same report, and emits one event if the batch is non-empty. The batching reduces event-thread switching when datanodes report many pending command statuses.

## State And Persistence
The handler is stateless. It creates transient wrapper payloads and does not persist command status itself. Downstream DELETE_BLOCK_STATUS consumers own state updates such as block deletion acknowledgements and metrics.

## Dependencies And Integration Points
Depends on heartbeat dispatcher payloads, protobuf `CommandStatus` and `SCMCommandProto.Type`, SCM event names, the event publisher, datanode identity, and ID generation for event payloads. It is a routing bridge between datanode heartbeat reports and delete-block status handling.

## Risks And Test Signals
Only delete-block command statuses are handled; new command types require explicit routing. Null report/list guards fail fast. Tests should verify batching, unsupported command logging behavior, emitted datanode identity, empty-list no-op behavior, and event IDs being generated for payloads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/command/CommandStatusReportHandler.java -->
