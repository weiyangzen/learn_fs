# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestCreatePipelineCommandHandler.java

## Purpose
`TestCreatePipelineCommandHandler` verifies Ratis pipeline creation command handling and idempotency when a pipeline already exists locally.

## Important APIs, Types, And Functions
- `CreatePipelineCommandHandler.handle` is the command entry point.
- `XceiverServerSpi.isExist` and `addGroup` represent local pipeline group creation.
- `RaftClient.getGroupManagementApi` and `GroupManagementApi.add` represent remote peer group creation.
- `CreatePipelineCommand` carries `PipelineID`, replication type/factor, and datanode list.

## Control Flow
Setup creates mocks for `OzoneContainer`, connection manager, Raft client, and group manager. The creation test builds a three-datanode RATIS pipeline, mocks local absence, calls the handler, verifies local `addGroup` with a zero priority list, and verifies group creation on the two non-local peers. The idempotency test mocks local existence and asserts neither local nor remote group addition is invoked.

## State And Persistence Behavior
State is Ratis group membership, mocked through write-channel and group-management APIs. No persistent data is written in the test.

## Dependencies And Integration Points
The test integrates SCM pipeline creation commands, Ozone write channel, Ratis group management, datanode context, and command handler executor behavior. Mockito lenient settings support broad setup without strict unused-stub failures.

## Risks And Edge Cases
Covered risks include duplicate pipeline creation, failing to add remote peer groups, and incorrect priority-list construction. It does not cover failures from Ratis APIs.

## Test Signals
Signals are direct verification of local `addGroup`, remote `add`, and zero calls under idempotent existing-pipeline conditions.
