# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestSCMDeleteBlocksCommandStatusManager.java

## Purpose

This unit test targets the nested `SCMDeleteBlocksCommandStatusManager`, which tracks SCM delete-block command IDs per datanode and maps each command to deleted-block transaction IDs until the command is sent, acknowledged, failed, or timed out.

## Important APIs, Types, and Functions

- `createScmCmdStatusData` creates `CmdStatusData` with default `TO_BE_SENT` state.
- `recordScmCommand` inserts command status under a datanode ID.
- `onSent` moves commands from `TO_BE_SENT` to `SENT`.
- `updateStatusByDNCommandStatus` reacts to DN heartbeat statuses `PENDING`, `EXECUTED`, and `FAILED`.
- `cleanTimeoutSCMCommand` and `cleanAllTimeoutSCMCommand` remove timed-out pending/sent records.

## Control Flow and State Behavior

`setup` creates two datanode IDs, four SCM command IDs, and four single-transaction sets. `testRecordScmCommand` verifies insertion and default state. `testOnSent` verifies the sent transition. Status-update tests record and send four commands, then simulate heartbeat reports: pending commands remain tracked as sent/pending execution, executed and failed commands are removed for downstream commit or resend processing. Cleanup tests use `Long.MAX_VALUE` to prove records do not expire early and `-1` to force timeout cleanup.

## State and Persistence

All state is in-memory within `manager.getScmCmdStatusRecord()`, a datanode-to-command map. The test does not touch the deleted-block DB; it isolates command-status lifecycle state.

## Dependencies and Integration Points

The test depends on `DatanodeID`, `StorageContainerDatanodeProtocolProtos.CommandStatus.Status`, and delete-service metrics. Production integration is with `DeletedBlockLogImpl` command creation, `onSent`, heartbeat status handling, and resend decisions.

## Risks and Test Signals

Risks include leaked command records, premature resend while a command is pending, or failure to resend failed/lost commands. Assertions inspect the exact map entries after each transition, giving precise state-machine coverage.
