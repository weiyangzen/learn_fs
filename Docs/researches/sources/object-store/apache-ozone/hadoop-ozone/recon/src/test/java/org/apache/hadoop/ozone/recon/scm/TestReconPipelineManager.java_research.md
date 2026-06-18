# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconPipelineManager.java

## Purpose
Tests Recon's pipeline manager initialization and stubbed pipeline factory. It verifies Recon can reconcile pipelines from SCM, update existing pipeline states, remove obsolete pipelines, accept new and duplicate additions, and expose no-op provider behavior.

## Important APIs, types, and functions
- Uses `ReconPipelineManager.newReconPipelineManager`, `initializePipelines`, `addPipeline`, `containsPipeline`, `getPipeline`, `getPipelines`, and `getPipelineFactory`.
- Builds `SCMNodeManager`, `SCMHAManagerStub`, `SCMContext`, `SCMSafeModeManager.SafeModeStatus`, `PipelineFactory`, and `ReconPipelineFactory.ReconPipelineProvider`.
- Uses generated `ReconSCMDBDefinition.PIPELINES` table.

## Control flow
Setup creates temp metadata, Recon storage config, DB store, SCM HA stub, and empty SCM context. `testInitialize` creates three SCM open pipelines, one Recon allocated pipeline with the same ID as an SCM pipeline, and one obsolete closed pipeline. It sets a leader/safe-mode-passed SCM context, adds old pipelines, calls `initializePipelines`, and verifies three final SCM pipelines, state update to OPEN, and obsolete removal. Other tests add a new pipeline, add a duplicate without exception, and inspect the pipeline factory type/providers.

## State and persistence behavior
Pipeline state is stored in the Recon SCM pipeline table and in the manager's runtime maps. Initialization should replace Recon's view with SCM's current view while preserving valid IDs through state updates and deleting stale records.

## Dependencies and integration points
The tests sit between Recon pipeline DB, SCM node manager, HA transaction buffering, safe-mode/leader context, and pipeline factory abstractions used by SCM container placement code.

## Risks and edge cases
Duplicate pipeline handling must remain idempotent. Initialization must not keep obsolete pipelines or fail to update allocated pipelines that SCM has opened. The stub factory should remain inert in Recon because Recon observes SCM pipelines rather than allocating them.

## Test signals
Signals are exact pipeline counts, `containsPipeline` checks for all SCM pipelines, state equality for updated pipelines, absence of obsolete pipeline ID, no exception on duplicate add, and factory/provider instance checks.
