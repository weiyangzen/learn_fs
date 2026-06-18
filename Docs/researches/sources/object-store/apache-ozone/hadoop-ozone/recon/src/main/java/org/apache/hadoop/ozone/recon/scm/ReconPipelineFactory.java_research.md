## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPipelineFactory.java

Purpose: this factory prevents Recon from creating or reading pipelines through SCM's pipeline provider path. Recon is a passive observer and should only ingest pipelines from SCM.

Important APIs and types: extends `PipelineFactory`, installs a defaulted map with `ReconPipelineProvider`, and defines provider methods for `create`, `createForRead`, and `close`.

Control flow: any attempt to create a pipeline or create a read pipeline throws `UnsupportedOperationException` with a clear Recon-specific message. `close` is a no-op.

State and persistence: no state or persistence. Its role is behavioral enforcement for `ReconPipelineManager`.

Dependencies and integration points: constructed by `ReconPipelineManager.newReconPipelineManager` and passed into `PipelineManagerImpl`. Normal Recon pipeline additions bypass creation and use `ReconPipelineManager.addPipeline` with SCM-supplied protobufs.

Risks and edge cases: if inherited SCM manager code unexpectedly calls `createForRead`, Recon will fail fast. This is intentional but can surface during upstream SCM behavior changes. The no-op close means pipeline removal must be handled by manager state operations.

Test signals: no direct test was found. Tests should assert all create paths throw and that manager initialization with this factory still permits SCM-sourced pipeline insertion.
