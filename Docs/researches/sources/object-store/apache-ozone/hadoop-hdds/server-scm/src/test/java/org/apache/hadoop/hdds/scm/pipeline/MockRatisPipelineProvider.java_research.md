# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockRatisPipelineProvider.java

Purpose: test subclass of `RatisPipelineProvider` that suppresses real datanode initialization and can force newly-created pipelines to remain allocated.

Important APIs and types: extends `RatisPipelineProvider`; constructors accept `NodeManager`, `PipelineStateManager`, `ConfigurationSource`, optional `EventPublisher`, and an `autoOpen` flag. Overrides `initializePipeline`, `create(RatisReplicationConfig)`, and `create(RatisReplicationConfig, List<DatanodeDetails>)`. Provides static `markPipelineHealthy`.

Control flow: `initializePipeline` is a no-op because test datanodes do not exist. If `autoOpenPipeline` is true, `create` delegates to the parent. If false, it delegates first, then rebuilds the pipeline with the same ID/nodes/config but state `ALLOCATED`. The node-list overload always returns an open pipeline from the provided nodes.

State and persistence behavior: the provider itself stores only the `autoOpenPipeline` flag. Pipeline state is embodied in returned `Pipeline` objects and persisted only when callers add them to `PipelineStateManager`. `markPipelineHealthy` mutates a pipeline object by reporting every datanode and setting the first node as leader.

Dependencies and integration points: depends on `RatisPipelineProvider`, SCM context, event publisher, pipeline state manager, and replication config conversion.

Risks and edge cases: default constructor without explicit `autoOpen` leaves the boolean default false, while the constructor with event publisher sets true; tests must choose the intended constructor. The rebuild path may omit fields from the parent-created pipeline if new fields are later added.

Test signals: fixture for tests needing deterministic open/allocated pipeline behavior without contacting datanodes.
