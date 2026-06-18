<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerProvider.java

Purpose: `WritableContainerProvider` defines the provider contract used by `WritableContainerFactory` to obtain a writable container for a new block.

Important APIs and types: Its single method is `getContainer(long size, T repConfig, String owner, ExcludeList excludeList)`. Implementations return an open `ContainerInfo` that can fit the requested block or throw `IOException`.

Control flow: The interface leaves selection, pipeline creation, container matching, and exclusion handling to implementations such as `WritableRatisContainerProvider` and `WritableECContainerProvider`.

State and persistence behavior: No state exists in the interface. Implementations mediate persisted state through `PipelineManager` and `ContainerManager`.

Dependencies and integration points: It is the abstraction between SCM block allocation and replication-specific writable container selection. It carries the owner and exclusion contract used by retry and placement paths.

Risks: The contract says returned containers must be open and large enough, but that is not enforceable at compile time. Implementations must consistently honor excluded datanodes, pipelines, and containers.

Test signals: Shared provider tests should validate capacity checks, owner matching, exclusion handling, exception behavior when no container can be allocated, and interaction with pipeline creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableContainerProvider.java -->
