<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/TopNOrderedContainerDeletionChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/TopNOrderedContainerDeletionChoosingPolicy.java

Purpose: default deletion policy that prioritizes containers with the most pending deletion blocks.

Important APIs and control flow: extends `ContainerDeletionChoosingPolicyTemplate`. Its comparator sorts `ContainerData` descending by `ContainerUtils.getPendingDeletionBlocks`, then inherited selection consumes the configured block budget across the ordered list.

State and persistence: stateless. The effective order depends on live pending-deletion counters from container metadata/statistics.

Dependencies and integration: used by `BlockDeletingService` as the default policy when no custom policy is configured. Depends on `ContainerUtils` and the template's budget selection.

Risks and test signals: tests should verify descending priority, partial selection of the last container when its pending count exceeds remaining budget, empty candidate behavior, and unsupported container-type filtering in upstream service. Containers with equal pending counts retain sort-dependent relative order and should not be assumed deterministic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/TopNOrderedContainerDeletionChoosingPolicy.java -->
