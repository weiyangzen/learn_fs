<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/PipelineChoosePolicyFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/PipelineChoosePolicyFactory.java

Purpose: `PipelineChoosePolicyFactory` instantiates the configured pipeline choose policy for regular or EC allocation, falling back to default random policies when configured classes fail.

Important APIs and types: `getPolicy(NodeManager, ScmConfig, boolean forEC)` reads `ScmConfig` policy class names, validates assignability to `PipelineChoosePolicy`, constructs with a no-arg constructor, and calls `init(NodeManager)`.

Control flow: The factory loads a class by name, attempts construction, and returns the initialized policy. If loading or construction fails for a non-default configured class, it logs the failure and retries the appropriate default. If the default itself fails, the exception is rethrown.

State and persistence behavior: The factory is stateless and persists nothing.

Dependencies and integration points: It is used during SCM initialization to wire block allocation policies. The configured class must be on the classpath, implement `PipelineChoosePolicy`, and expose a no-argument constructor.

Risks: Reflection errors become either `SCMException` for missing constructors or runtime exceptions for instantiation failures. Fallback can hide misconfiguration unless logs are monitored. Defaults for EC and non-EC currently both use random selection.

Test signals: Tests should cover valid custom policy loading, invalid class fallback, non-assignable class rejection, missing no-arg constructor errors, default failure propagation, and separate EC policy configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/PipelineChoosePolicyFactory.java -->
