<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PipelineEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PipelineEndpoint.java

## Purpose

`PipelineEndpoint` exposes `/pipelines` metadata for all Recon-known SCM pipelines, including optional Ratis leader-election metrics.

## Important APIs and Types

`getPipelines` returns `PipelinesResponse` containing `PipelineMetadata` records. Each record includes pipeline id, datanodes, duration, state, replication config, leader node, container count, leader election count, and last leader election elapsed time when metrics are configured.

## Control Flow

The endpoint iterates `ReconPipelineManager.getPipelines`, copies nodes, computes age from creation timestamp, best-effort resolves leader host and container count, then optionally builds a Ratis group id from the UUID suffix and queries the metrics provider for election metrics.

## State and Persistence

The endpoint is read-only. Pipeline state comes from Recon SCM in-memory managers, and metrics come from the external metrics provider.

## Dependencies and Integration Points

It depends on `ReconPipelineManager`, `MetricsServiceProviderFactory`, `MetricsServiceProvider`, Ratis metric names, and `PipelineMetadata` DTOs.

## Risks and Edge Cases

The group-id derivation assumes the Ratis metric label uses `group-<last UUID segment uppercase>`. Metric values are cast to `TreeMap<Double, Double>`, so provider shape changes can fail at runtime. Leader or container-count failures are logged and produce partial metadata.

## Test Signals

Tests should cover no metrics provider, provider query success/failure, leader lookup failure, container-count failure, group-id derivation, and stable serialization of replication configs and datanode lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/PipelineEndpoint.java -->
