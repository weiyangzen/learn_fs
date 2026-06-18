<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineProvider.java

Purpose: `RatisPipelineProvider` creates and closes Ratis replication pipelines for SCM. It selects datanodes, enforces configured pipeline limits, chooses an optional suggested leader, and publishes create/close pipeline commands to datanodes.

Important APIs and types: The provider extends `PipelineProvider<RatisReplicationConfig>` and implements `create` overloads, `createForRead`, and `close`. It uses `NodeManager`, `PipelineStateManager`, `PlacementPolicy`, `PipelinePlacementPolicyFactory`, `LeaderChoosePolicyFactory`, `SCMContext`, `CreatePipelineCommand`, `ClosePipelineCommand`, and `SCMEvents.DATANODE_COMMAND`.

Control flow: `create` first checks global or per-datanode Ratis pipeline limits for factor THREE. Factor ONE chooses unused nodes directly, while factor THREE excludes datanodes already at their pipeline engagement limit before calling placement. It then chooses a suggested leader, builds an ALLOCATED pipeline, stamps the SCM leader term on a `CreatePipelineCommand`, and fires that command to each datanode. `close` similarly sends a term-stamped `ClosePipelineCommand` to all pipeline members.

State and persistence behavior: This class builds `Pipeline` objects but does not add them to state or persist them; the manager that called it owns that. It reads pipeline and node state to enforce limits, uses configuration for container and Ratis-volume free-space thresholds, and embeds the current SCM term in datanode commands.

Dependencies and integration points: It integrates placement policy, node health, HA context, event publishing, and leader-selection policy. `WritableRatisContainerProvider` depends on the manager path that uses this provider to create a pipeline before allocating containers.

Risks: Pipeline limit calculations combine active, closed, factor ONE, and healthy node counts and can block creation if counters are stale. The method mutates the `excludedNodes` list when adding engagement exclusions, which is risky if callers pass a shared mutable list. Command publication assumes SCM is leader and the event queue will deliver commands reliably.

Test signals: Tests should cover factor ONE and THREE placement, limit enforcement, leader policy selection, exclusion of engaged datanodes, event publication counts and command terms, and close command fan-out.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineProvider.java -->
