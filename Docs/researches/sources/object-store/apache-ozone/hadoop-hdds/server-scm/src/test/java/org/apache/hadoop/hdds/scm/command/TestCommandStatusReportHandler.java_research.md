# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/command/TestCommandStatusReportHandler.java

## Purpose

This test verifies `CommandStatusReportHandler`, the event handler that processes datanode heartbeat command-status reports and fires SCM events for command-specific status consumers. The test concentrates on delete-block status reporting and log-visible event publication.

## Important APIs, Types, and Functions

- `CommandStatusReportHandler.onMessage` is the handler under test.
- `CommandStatusReportFromDatanode` wraps a datanode and `CommandStatusReportsProto`.
- `HddsTestUtils.createCommandStatusReport` builds heartbeat report protos.
- The test class implements `EventPublisher.fireEvent` and logs fired events for assertion.
- `getCommandStatusList` creates `deleteBlocksCommand` and `replicateContainerCommand` statuses.

## Control Flow and State Behavior

The first report contains an empty status list and should produce no delete-block or replicate-command event log entries. The second report contains executed delete-block status and failed replicate-container status. `onMessage` is expected to publish events, which the test observes by capturing this test class's logger output and checking for `Delete_Block_Status` and `deleteBlocksCommand`.

## State and Persistence

There is no persistent state. The only state is the captured logger buffer and synthesized command-status protos.

## Dependencies and Integration Points

The file depends on SCM heartbeat dispatcher payloads, datanode details, command-status protobufs, `HddsIdFactory`, `HddsTestUtils`, event publishing, and `GenericTestUtils.LogCapturer`. Production integration is with datanode heartbeat handling and downstream consumers such as deleted-block transaction status management.

## Risks and Test Signals

The test is log-based, so message wording changes can affect it even if events still fire. It gives useful signal that empty reports are ignored and non-empty reports dispatch command-specific events.
