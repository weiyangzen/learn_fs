<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicyFactory.java

Purpose: `LeaderChoosePolicyFactory` instantiates the configured Ratis pipeline leader choose policy.

Important APIs and types: `getPolicy(ConfigurationSource, NodeManager, PipelineStateManager)` reads `OZONE_SCM_PIPELINE_LEADER_CHOOSING_POLICY`, defaults to `MinLeaderCountChoosePolicy`, requires a `(NodeManager, PipelineStateManager)` constructor, and returns a constructed policy.

Control flow: The factory obtains the class through configuration, looks up the required constructor, logs the selected type, and invokes it. Missing constructor is converted to `SCMException`; constructor invocation failures become runtime exceptions.

State and persistence behavior: The factory is stateless and persists nothing.

Dependencies and integration points: It is called by `RatisPipelineProvider` during provider construction. Custom policies must be classpath-visible and implement the expected constructor signature.

Risks: Unlike `PipelineChoosePolicyFactory`, there is no fallback after an invalid configured class once configuration resolves it. Provider construction wraps exceptions in `RuntimeException`, which can fail SCM startup.

Test signals: Tests should cover default policy creation, custom policy creation, missing constructor errors, non-policy class rejection via config, and startup failure propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/leader/choose/algorithms/LeaderChoosePolicyFactory.java -->
