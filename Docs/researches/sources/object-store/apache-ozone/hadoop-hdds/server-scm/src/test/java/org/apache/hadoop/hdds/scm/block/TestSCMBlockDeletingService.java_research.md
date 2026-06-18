# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMBlockDeletingService.java

## Purpose

This unit test validates `SCMBlockDeletingService`, the background SCM service that scans the deleted-block log and publishes `deleteBlocksCommand` events for eligible datanodes. It focuses on command fan-out and queue-limit filtering.

## Important APIs, Types, and Functions

- `SCMBlockDeletingService.getTasks().poll().call()` triggers one scanner execution.
- `getDatanodesWithinCommandLimit` filters datanodes by pending delete-command counts.
- `DeletedBlockLog.getTransactions` is mocked to return `DatanodeDeletedBlockTransactions`.
- `EventPublisher.fireEvent` is verified for `SCMEvents.DATANODE_COMMAND`.
- `ScmBlockDeletingServiceMetrics` counters are asserted after command publication.

## Control Flow and State Behavior

`setup` mocks `NodeManager`, `EventPublisher`, `SCMContext`, and `SCMServiceManager`. It creates three random healthy datanodes, associates the same synthetic `DeletedBlocksTransaction` with each DN, and configures the deleted-block log to return those assignments. The service is spied so `shouldRun` returns true. `testCall` executes one task and captures three `CommandForDatanode` events, proving one command is emitted to each healthy DN and metrics count both commands and transactions. `testLimitCommandSending` changes `NodeManager.getTotalDatanodeCommandCount` to simulate full and empty queues and verifies inclusion/exclusion.

## State and Persistence

There is no persistent state. Service state is in memory, metrics are registered for the test and unregistered afterward, and the mocked deleted-block transaction set is fixed.

## Dependencies and Integration Points

The test integrates `SCMBlockDeletingService` with `DeletedBlockLog`, `NodeManager`, `DatanodeConfiguration` queue limits, SCM event publishing, command protos, metrics, reconfiguration handler, and service lifecycle.

## Risks and Test Signals

Risk areas are overloading datanodes with delete commands, dropping eligible datanodes, and incorrect metrics. The event-captor assertions and queue-limit boundary checks provide direct signals for the scanner's external behavior.
