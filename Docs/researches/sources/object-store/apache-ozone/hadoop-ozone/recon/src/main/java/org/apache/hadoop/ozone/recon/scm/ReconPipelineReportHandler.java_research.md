## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineReportHandler.java

Purpose: this handler processes DataNode pipeline reports in Recon, backfilling unknown pipelines from SCM before applying shared SCM report updates.

Important APIs and types: extends `PipelineReportHandler`, stores a `StorageContainerServiceProvider`, and overrides `processPipelineReport(PipelineReport, DatanodeDetails, EventPublisher)`.

Control flow: on a pipeline report, it derives `PipelineID`. If the pipeline is unknown locally, it calls `scmServiceProvider.getPipeline`; if SCM returns a remote `PipelineNotFoundException`, it rethrows that condition. Once the pipeline exists, it marks the reporting datanode and leader ID using inherited helpers. ALLOCATED pipelines are opened when the pipeline becomes healthy.

State and persistence: unknown pipelines fetched from SCM are persisted by `ReconPipelineManager.addPipeline`. Reported datanode and leader information are stored in the in-memory/persistent pipeline state managed by the parent.

Dependencies and integration points: registered by the facade for `SCMEvents.PIPELINE_REPORT`; works with `ReconPipelineManager`, `ReconSafeModeManager`, and SCM context. It is one of the ways Recon learns pipelines missed during startup or sync.

Risks and edge cases: an unknown pipeline that no longer exists in SCM produces a not-found path and may drop the report. Network or SCM RPC errors propagate to the event handler. Healthy transition from ALLOCATED to OPEN mirrors SCM behavior but in a passive context.

Test signals: no direct test was found. Useful tests should mock SCM pipeline lookup success, remote not-found unwrapping, and ALLOCATED healthy opening.
