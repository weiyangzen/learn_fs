<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/MinLeaderCountChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/MinLeaderCountChoosePolicy.java

Purpose: `MinLeaderCountChoosePolicy` balances suggested Ratis leaders by choosing the datanode with the fewest current non-closed pipelines where it is already the suggested leader.

Important APIs and types: It extends `LeaderChoosePolicy` and uses `NodeManager.getPipelines(DatanodeDetails)`, `PipelineStateManager.getPipeline`, `Pipeline.getSuggestedLeaderId`, and `PipelineID`.

Control flow: `chooseLeader` builds a count map for input datanodes, scans each datanode's pipeline IDs, increments the count for non-closed pipelines whose suggested leader ID matches the datanode, and returns the datanode with the smallest count.

State and persistence behavior: The policy stores no derived state. It reads live node and pipeline manager state.

Dependencies and integration points: `RatisPipelineProvider` writes the returned datanode into pipeline metadata and `CreatePipelineCommand`. The policy depends on previous pipelines preserving suggested leader IDs.

Risks: Ties are resolved by map iteration order, which is not explicitly stable. Missing pipeline IDs from node manager are logged at debug and ignored. It balances suggested leaders, not actual Ratis elected leaders.

Test signals: Tests should cover minimum-count selection, closed pipeline exclusion, missing pipeline tolerance, tie behavior, and command metadata containing the chosen leader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/MinLeaderCountChoosePolicy.java -->
