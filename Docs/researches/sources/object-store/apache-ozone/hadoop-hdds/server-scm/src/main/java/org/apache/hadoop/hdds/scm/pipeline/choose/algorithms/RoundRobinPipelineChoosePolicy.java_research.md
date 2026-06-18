<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RoundRobinPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RoundRobinPipelineChoosePolicy.java

Purpose: `RoundRobinPipelineChoosePolicy` selects candidate pipelines in cyclic order. The class comment positions it mainly as a debugging and testing policy.

Important APIs and types: It implements `PipelineChoosePolicy.choosePipeline` and synchronized `choosePipelineIndex`, maintaining `nextPipelineIndex`.

Control flow: Each index selection normalizes `nextPipelineIndex` modulo list size, returns the current index, then increments the counter. `choosePipeline` indexes into the list with that result.

State and persistence behavior: The only state is the in-memory next index. It is not persisted, so order restarts with the object.

Dependencies and integration points: It can be selected through the policy factory for deterministic spreading across available pipelines.

Risks: Empty lists cause division by zero in `choosePipelineIndex`. The index is global to the policy instance, not keyed by replication config or owner, so changing candidate lists can produce non-obvious ordering.

Test signals: Tests should cover cyclic selection, synchronized concurrent calls, behavior when the candidate list shrinks, and explicit empty-list failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/RoundRobinPipelineChoosePolicy.java -->
