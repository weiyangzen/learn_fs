# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableRatisContainerProvider.java

## Purpose
`TestWritableRatisContainerProvider` verifies the simpler Ratis writable-container selection path: prefer a writable container in an existing open pipeline, skip pipelines without matching containers, create a new pipeline/container when necessary, and propagate failures when creation cannot provide a container.

## Important APIs, Types, and Functions
- `WritableRatisContainerProvider.getContainer` is the core API.
- Mocks for `PipelineManager` and `ContainerManager` define existing pipelines, matching-container responses, and pipeline creation.
- Helpers `existingPipelines`, `pipelineHasContainer`, `createNewContainerOnDemand`, and `throwWhenCreatePipeline` encode the test scenarios.

## Control Flow
The tests first set up mocked open pipeline lists for `RatisReplicationConfig(THREE)`. If a pipeline has a matching container, the provider returns it and does not create a pipeline. If no usable container exists, `createPipeline` is expected, followed by a second open-pipeline scan that returns the new container. Failure test makes `createPipeline` throw `SCMException`.

## State and Persistence Behavior
There is no real persistence; state is Mockito stubbing plus an `AtomicLong` for container IDs. Verification of call counts is the main state signal.

## Dependencies and Integration Points
The class integrates with `RandomPipelineChoosePolicy`, `PipelineManager.getPipelines(repConfig, OPEN, emptySet, emptySet)`, `ContainerManager.getMatchingContainer`, and `PipelineManager.createPipeline(repConfig)`.

## Risks and Edge Cases
The repeated test runs 100 times to catch random policy ordering problems when one pipeline lacks a container. Exclude-list behavior is not explored beyond the no-exclusion constant.

## Test Signals
The exact Mockito verifications distinguish reuse from creation: existing-container paths call `getPipelines` once and never create, while creation paths call `getPipelines` twice and create once.
