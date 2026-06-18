<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/HealthyPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/HealthyPipelineChoosePolicy.java

Purpose: `HealthyPipelineChoosePolicy` wraps random selection with a health preference. It keeps choosing random pipelines until it finds a healthy one, and returns the last unhealthy candidate as fallback if none are healthy.

Important APIs and types: It implements `PipelineChoosePolicy` with `choosePipeline` and `choosePipelineIndex`, delegates to `RandomPipelineChoosePolicy`, and checks `Pipeline.isHealthy()`.

Control flow: The method mutates the supplied candidate list by removing unhealthy selected pipelines until a healthy pipeline is found or the list is empty. `choosePipelineIndex` protects callers by copying the input before mutation and then resolving the chosen pipeline against the original list.

State and persistence behavior: No persistent state exists. Runtime state is only the random policy instance.

Dependencies and integration points: It is used directly or as a component of capacity-based selection. It depends on pipeline health state being up to date.

Risks: Direct callers of `choosePipeline` may be surprised that the input list is modified. Empty lists return `null` via fallback, and downstream policies must handle that. Returning one unhealthy fallback can still allocate against an unhealthy pipeline if callers do not recheck.

Test signals: Tests should cover healthy selection, all-unhealthy fallback, list mutation in direct calls, non-mutation through `choosePipelineIndex`, and empty-list behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/HealthyPipelineChoosePolicy.java -->
