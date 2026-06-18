<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RandomPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RandomPipelineChoosePolicy.java

Purpose: `RandomPipelineChoosePolicy` selects a pipeline uniformly at random from the candidate list.

Important APIs and types: It implements `PipelineChoosePolicy.choosePipeline` and `choosePipelineIndex`, using `ThreadLocalRandom`.

Control flow: `choosePipelineIndex` returns `-1` for an empty list or a random integer in `[0, size)`. `choosePipeline` immediately indexes into the list using the returned index.

State and persistence behavior: The policy is stateless and stores no decisions.

Dependencies and integration points: It is the default policy from `PipelineChoosePolicyFactory` and the delegate used by `HealthyPipelineChoosePolicy`.

Risks: Calling `choosePipeline` with an empty list throws because it uses index `-1`; callers that may have no candidates should use or check `choosePipelineIndex` first. It ignores size, owner, utilization, and health unless composed by another policy.

Test signals: Tests should assert valid index ranges, empty-list `-1` from `choosePipelineIndex`, exception behavior for direct empty `choosePipeline`, and broad distribution sanity if needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RandomPipelineChoosePolicy.java -->
