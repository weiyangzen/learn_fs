<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicy.java

Purpose: `LeaderChoosePolicy` is the abstract base for policies that may suggest a Ratis leader from selected datanodes.

Important APIs and types: It stores `NodeManager` and `PipelineStateManager`, exposes protected getters, and defines abstract `chooseLeader(List<DatanodeDetails>)`.

Control flow: Concrete subclasses implement all choice behavior. The base only supplies manager access.

State and persistence behavior: The base holds references to current SCM managers and persists nothing.

Dependencies and integration points: `LeaderChoosePolicyFactory` constructs subclasses, and `RatisPipelineProvider` consumes their output while building create commands and pipeline metadata.

Risks: Subclasses can return `null`; callers must treat that as a valid "no suggestion" path. Manager references may reflect changing cluster state during selection.

Test signals: Subclass tests should verify access to manager state and caller handling of both concrete datanode and null leader choices.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicy.java -->
