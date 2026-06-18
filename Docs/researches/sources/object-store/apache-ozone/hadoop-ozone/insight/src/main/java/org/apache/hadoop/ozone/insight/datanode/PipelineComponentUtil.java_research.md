<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/PipelineComponentUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/PipelineComponentUtil.java

Purpose: utility for resolving a pipeline filter into datanode components for pipeline/Ratis insight.

Important APIs: constant `PIPELINE_FILTER = "pipeline"`. `getPipelineIdFromFilters` requires a `pipeline` filter and returns its value. `withDatanodesFromPipeline(scmClient, pipelineId, func)` lists SCM pipelines, finds the matching UUID string, builds a `DATANODE` component for each datanode using uuid, hostname, and hardcoded port 9882, and applies the callback.

Control flow and integration: `RatisInsight` opens an SCM client, retrieves the pipeline id from filters, then uses this utility to add loggers for every datanode in the pipeline.

State and persistence: stateless. Reads live SCM pipeline state through `ScmClient`.

Risks and tests: hardcoded port 9882 ignores HTTP policy and datanode HTTP config. The error message says "No such multi-node pipeline" even for any missing pipeline. The callback return value is ignored and exceptions are not specially handled. No direct tests cover pipeline lookup or missing filters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/PipelineComponentUtil.java -->
