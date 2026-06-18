<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/RatisInsight.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/RatisInsight.java

Purpose: insight point for one datanode Ratis pipeline/ring.

Important APIs: constructor stores `OzoneConfiguration`. `getRelatedLoggers` creates an SCM client, resolves the required `pipeline` filter, enumerates datanodes through `PipelineComponentUtil`, and adds logger `org.apache.ratis.server` for each datanode at TRACE or DEBUG. `getDescription` describes the ring. `filterLog` returns true.

Control flow and integration: depends on SCM client address, live pipeline list, and datanode logstream endpoints. It exposes log insight only; it does not define metrics or config classes.

State and persistence: holds configuration. No persistence. Uses try-with-resources to close `ScmClient`.

Risks and tests: `IOException` becomes `UncheckedIOException`, while invalid/missing filters throw `IllegalArgumentException`. Datanode endpoint resolution inherits the hardcoded port behavior from `PipelineComponentUtil`. No direct tests cover Ratis insight.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/datanode/RatisInsight.java -->
