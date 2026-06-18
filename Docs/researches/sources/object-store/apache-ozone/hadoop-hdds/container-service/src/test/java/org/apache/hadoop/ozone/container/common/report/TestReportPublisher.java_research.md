# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/report/TestReportPublisher.java

## Purpose
`TestReportPublisher` validates base `ReportPublisher` scheduling behavior and command-status report generation. It verifies periodic execution, full-report refresh into `StateContext`, and `CommandStatusReportPublisher` handling of pending/executed command statuses.

## Important APIs, Types, And Functions
- `ReportPublisher.init` schedules the publisher at fixed rate.
- `ReportPublisher.run` calls subclass `getReport` and pushes the result to `StateContext.refreshFullReport`.
- `DummyReportPublisher` overrides `getReportFrequency` and `getReport`, counting invocations.
- `CommandStatusReportPublisher.getReport` reads `StateContext.getCommandStatusMap` and builds command status protobuf reports.
- `CommandStatus.CommandStatusBuilder`, `SCMCommandProto.Type`, and `CommandStatus.Status` provide report content.

## Control Flow
One test verifies `init` calls `scheduleAtFixedRate` with initial delay and frequency. Scheduling tests use a daemon `ScheduledExecutorService`, sleep long enough for one or two runs, then shut down the executor and assert no more report calls happen. `testPublishReport` verifies a scheduled run refreshes the full report in `StateContext`. The command-status test starts with an empty map and expects `null`, inserts one pending delete-block command and one executed close-container command, then asserts the report contains two statuses.

## State And Persistence Behavior
State is in-memory: scheduled executor tasks, a report invocation counter, and a concurrent command-status map. No persistent storage is used.

## Dependencies And Integration Points
The suite depends on Hadoop executor helpers, Guava `ThreadFactoryBuilder`, protobuf `Message`, `StateContext`, and command status model classes. It verifies the link between datanode command execution status and heartbeat report publication.

## Risks And Edge Cases
Covered risks include publisher not scheduling, scheduled execution continuing after shutdown, `StateContext` not receiving reports, empty command status maps producing empty/no reports, and command statuses not being included. Timing-based sleeps can be somewhat brittle but frequencies are short and assertions are simple.

## Test Signals
Signals include schedule verification, invocation counts before/after shutdown, `refreshFullReport` verification, and command status count assertions.
