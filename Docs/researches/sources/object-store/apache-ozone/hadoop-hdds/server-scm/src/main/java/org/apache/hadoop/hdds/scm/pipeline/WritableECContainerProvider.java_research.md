<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableECContainerProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableECContainerProvider.java

Purpose: `WritableECContainerProvider` selects or creates writable containers for erasure-coded block groups. It maintains an open EC pipeline pool sized by configured minimums and healthy volume count, and it assumes one open container per EC pipeline.

Important APIs and types: Public API is `getContainer`. Key helpers are `getMaximumPipelines`, `allocateContainer`, `pipelineIsExcluded`, `getContainerFromPipeline`, `containerHasSpace`, and nested `WritableECContainerProviderConfig`. It uses `NodeManager`, `PipelineManager`, `ContainerManager`, `PipelineChoosePolicy`, `ECReplicationConfig`, and `ExcludeList`.

Control flow: `getContainer` first calculates the maximum open pipelines. Under provider synchronization, it tries to allocate a fresh pipeline/container if the current open count is below the limit. If not, it chooses among existing open pipelines using the policy, synchronizes per pipeline ID, fetches the associated container, closes pipelines with no suitable container or insufficient space, skips excluded resources, updates last-used time, and returns. If all existing pipelines fail, it may raise the limit up to healthy node count for a final allocation attempt.

State and persistence behavior: The provider itself persists nothing. Pipeline and container creation, opening, closing, and lookup are delegated to SCM managers. Reconfigurable config state includes minimum EC pipelines and pipeline-per-volume factor; validation normalizes negative factors back to default.

Dependencies and integration points: It depends on accurate healthy volume counts, pipeline state, container used bytes, and container size configuration. It integrates with the EC pipeline choose policy and SCM reconfiguration handler.

Risks: Open count is updated locally after closing unsuitable pipelines and can diverge from concurrent manager state. Synchronizing on `pipeline.getId()` only coordinates callers that use the same ID object equality path. A null container after new pipeline creation is treated defensively as an error even though placement should have checked space.

Test signals: Tests should cover minimum and volume-derived limits, negative factor validation, fresh allocation, existing pipeline reuse, exclusion of container/pipeline/datanode, close-on-full or missing container, last-used updates, and final limit expansion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/WritableECContainerProvider.java -->
