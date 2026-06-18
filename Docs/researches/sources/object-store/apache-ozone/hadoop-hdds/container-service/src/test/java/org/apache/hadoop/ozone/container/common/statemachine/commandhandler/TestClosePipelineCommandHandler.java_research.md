# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestClosePipelineCommandHandler.java

## Purpose
`TestClosePipelineCommandHandler` verifies Ratis pipeline close command handling, idempotency when a pipeline is already absent, and duplicate-suppression while a close is in progress.

## Important APIs, Types, And Functions
- `ClosePipelineCommandHandler.handle`, `isPipelineCloseInProgress`, and `getInvocationCount` are under test.
- `XceiverServerRatis.isExist`, `removeGroup`, `getRaftPeersInPipeline`, `getShouldDeleteRatisLogDirectory`, and `getServer` are mocked.
- `RaftClient.getGroupManagementApi` and `GroupManagementApi.remove` represent peer-side group removal.
- `RatisHelper.toRaftPeer` and `toRaftPeerId` convert datanode identities.

## Control Flow
The main close test creates a three-node pipeline where the current datanode is one member. The handler removes the local Ratis group and calls the group-management API for the other two peers, passing deletion flags derived from the write channel. The idempotency test sets `isExist` to false and verifies no remove operations happen. The pending-close test blocks the first `removeGroup` call using latches, submits a duplicate command for the same pipeline, releases the first call, and asserts only one invocation was processed and the in-progress flag is cleared.

## State And Persistence Behavior
State under test is local in-memory duplicate tracking for pipeline UUIDs and Ratis group membership side effects. Actual Ratis logs are not persisted, but the delete-log-directory flag is passed through and verified.

## Dependencies And Integration Points
This file integrates SCM close-pipeline commands with `OzoneContainer` write channel, Ratis server/group APIs, `SCMConnectionManager`, and `StateContext`. It is a boundary test for local and remote Ratis group cleanup.

## Risks And Edge Cases
Covered risks include duplicate command execution, removing a non-existent pipeline, in-progress flag leaks, and incorrect propagation of log directory deletion behavior to remote peer removals.

## Test Signals
Signals are `removeGroup` call counts, `GroupManagementApi.remove` call counts and arguments, in-progress boolean assertions, executor termination, and invocation count.
