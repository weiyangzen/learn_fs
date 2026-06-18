<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/DefaultLeaderChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/DefaultLeaderChoosePolicy.java

Purpose: `DefaultLeaderChoosePolicy` deliberately does not suggest a Ratis leader. Returning `null` lets Ratis elect a leader without SCM-imposed priority.

Important APIs and types: It extends `LeaderChoosePolicy` and implements `chooseLeader(List<DatanodeDetails>)` by returning `null`.

Control flow: Construction passes `NodeManager` and `PipelineStateManager` to the base class. Leader choice ignores the datanode list.

State and persistence behavior: No mutable or persisted state exists beyond the base references.

Dependencies and integration points: `RatisPipelineProvider` interprets `null` as a create command without suggested leader. The policy can be selected via `LeaderChoosePolicyFactory`.

Risks: Deployments expecting leader balancing should use a different policy. Tests must distinguish "no suggested leader" from an error.

Test signals: Tests should assert null leader return and that create commands omit suggested leader when this policy is configured.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/DefaultLeaderChoosePolicy.java -->
