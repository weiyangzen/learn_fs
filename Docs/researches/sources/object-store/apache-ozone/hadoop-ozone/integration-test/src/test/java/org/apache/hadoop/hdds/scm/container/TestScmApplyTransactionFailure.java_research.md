<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestScmApplyTransactionFailure.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestScmApplyTransactionFailure.java

Purpose: Validates failure handling in SCM HA state-machine transaction application for invalid container and pipeline mutations.

Important APIs and types: Uses `HATests.TestCase`, leader `StorageContainerManager`, `ContainerManager`, `PipelineManagerImpl`, `PipelineState`, `ContainerInfoProto`, `SCMException`, `StateMachineException`, `InvalidPipelineStateException`, and `DuplicatedPipelineIdException`.

Control flow: `BeforeAll` captures the leader's managers. One test closes an open Ratis three pipeline, creates a container protobuf referencing it, calls `ContainerStateManager.addContainer`, and verifies a nested exception chain plus absence of the container. It then allocates another container to prove the state machine still works. The second test replays an existing pipeline protobuf through the state manager and expects duplicate-ID failure.

State and persistence behavior: The rejected transactions must not mutate SCM metadata: the failed container ID remains absent and duplicate pipeline insertion does not replace existing state. The final allocation check confirms subsequent Ratis-applied transactions continue.

Dependencies and integration points: Covers SCM HA Ratis state-machine wrapping, pipeline state validation, container-state persistence, pipeline-state persistence, and exception propagation across the manager APIs.

Risks: The helper constructs container ID `1`, which assumes that ID is available in the HA fixture. Assertions depend on exact cause nesting: `SCMException` caused by `StateMachineException` caused by the domain exception.

Test signals: Signals include expected exception classes in order, `ContainerNotFoundException` after rejected add, successful allocation after a rejected transaction, and duplicate pipeline ID rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestScmApplyTransactionFailure.java -->
