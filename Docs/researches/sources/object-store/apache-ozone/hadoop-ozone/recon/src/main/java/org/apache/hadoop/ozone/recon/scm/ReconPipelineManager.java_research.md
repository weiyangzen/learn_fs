## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineManager.java

Purpose: `ReconPipelineManager` is Recon's passive pipeline metadata manager, backed by SCM's pipeline state machinery but with creation disabled and explicit SCM-sourced initialization.

Important APIs and types: `newReconPipelineManager` builds a `PipelineStateManagerImpl` from the pipeline table, node manager, HA/Ratis stubs, and DB transaction buffer, then uses `ReconPipelineFactory`. `initializePipelines`, `removeInvalidPipelines`, `addPipeline`, and `addContainerToPipeline` are the Recon-specific methods.

Control flow: `initializePipelines` takes the SCM pipeline list, adds missing pipelines, updates existing state and creation timestamp, then removes pipelines that are present locally but absent from SCM. Invalid non-closed pipelines are first marked closed before `closePipeline` and `deletePipeline`. `addPipeline` acquires a write lock and inserts the SCM protobuf if absent. `addContainerToPipeline` forces container association through the state manager.

State and persistence: pipeline state is persisted in the `PIPELINES` column family provided by `ReconSCMDBDefinition`. Container membership in pipelines is maintained through the inherited pipeline state manager. Reinitialization occurs indirectly from the facade after SCM DB snapshot replacement.

Dependencies and integration points: used by report handlers, stale/dead handlers, `PipelineSyncTask`, `ReconContainerManager`, and container/pipeline API surfaces. It depends on `ReconPipelineFactory` to prevent active SCM behavior.

Risks and edge cases: `pipelinesFromScm.contains(p)` relies on `Pipeline.equals`; if equality includes mutable fields, invalid-removal decisions may be surprising. Removing absent pipelines may lose historical pipeline metadata Recon might otherwise display. Forced container-to-pipeline association bypasses some parent validation to match passive ingestion needs.

Test signals: pipeline behavior is indirectly covered by SCM facade and sync tests. Focused tests should cover add idempotency, state/timestamp refresh, invalid pipeline removal, and forced container association.
