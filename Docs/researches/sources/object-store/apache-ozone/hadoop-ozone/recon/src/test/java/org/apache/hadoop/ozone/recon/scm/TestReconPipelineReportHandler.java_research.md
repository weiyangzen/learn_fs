# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineReportHandler.java

## Purpose
Tests Recon's pipeline report handler for known and unknown pipeline IDs reported by datanodes. It ensures Recon fetches and adds a missing pipeline from SCM but does not re-add a pipeline that it already tracks.

## Important APIs, types, and functions
- Exercises `ReconPipelineReportHandler.processPipelineReport`.
- Uses mocked `ReconPipelineManager`, `StorageContainerServiceProvider`, `PipelineReport`, `EventPublisher`, and `ReconSafeModeManager`.
- Converts `PipelineID` to protobuf for the report and SCM service-provider lookup.

## Control flow
The test first stubs a pipeline that is absent from Recon but available from SCM, processes a report for it, and verifies `addPipeline` and `getPipeline` are called. It then stubs another pipeline as already contained in Recon, processes a second report, and verifies no add occurs while the pipeline is still looked up.

## State and persistence behavior
The file uses mocks only, so no actual DB state is mutated. It validates the handler's decision boundary for when to mutate the real pipeline manager.

## Dependencies and integration points
This handler is part of datanode heartbeat processing and bridges pipeline reports to Recon's SCM pipeline cache, with SCM RPC fallback for missing pipeline definitions.

## Risks and edge cases
The test depends on Mockito call counts and reused mocks. A behavior change that performs additional lookups or handles missing SCM pipeline responses differently may need adjusted assertions.

## Test signals
Signals are exact `addPipeline` and `getPipeline` invocation counts for missing versus already-known pipeline reports.
