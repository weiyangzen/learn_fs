# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/InfoSubcommand.java

## Purpose
Implements `ozone admin container info`, printing container metadata, pipeline information, write pipeline state, datanodes, and replicas for one or more container IDs.

## Important APIs, Types, And Functions
Options include `--json` and `ContainerIDParameters`. It uses `getContainerWithPipeline`, `getContainerReplicas`, `getPipeline`, JSON wrappers `ContainerWithPipelineAndReplicas`/`ContainerWithoutDatanodes`, and `PipelineWithoutDatanodes` for empty pipelines.

## Control Flow
The command validates all IDs first, optionally prints JSON array delimiters for multiple IDs, then processes each container. It fetches container/pipeline data, separately tries replica fetch, handles missing write pipeline as CLOSED, and prints text or JSON.

## State And Persistence
Read-only against SCM/container metadata. It maintains only output formatting flags.

## Dependencies And Integration Points
Depends on SCM container and pipeline APIs, `SCMHAUtils.unwrapException`, `PipelineNotFoundException`, `HddsUtils.formatAccessControlExceptionLine`, `JsonUtils`, and `ContainerReplicaInfo`.

## Risks And Test Signals
Per-container lookup failures are printed and processing continues, possibly with successful exit. JSON for multiple containers is manually comma-delimited and can be invalid if an item prints only an error. Tests should cover multiple IDs, missing container, missing replica info, closed write pipeline, authorization errors, empty pipeline JSON, and replica sorting.
