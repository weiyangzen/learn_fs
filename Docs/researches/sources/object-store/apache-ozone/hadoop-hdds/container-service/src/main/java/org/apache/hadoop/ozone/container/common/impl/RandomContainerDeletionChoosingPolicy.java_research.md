<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/RandomContainerDeletionChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/RandomContainerDeletionChoosingPolicy.java

Purpose: deletion policy that randomizes the order of candidate containers before the shared selection template allocates a delete-block budget.

Important APIs and control flow: extends `ContainerDeletionChoosingPolicyTemplate` and implements `orderByDescendingPriority` by calling `Collections.shuffle(candidateContainers)`. The inherited template filters positive pending-delete counts, caps each selected container by remaining block budget, and returns `ContainerBlockInfo` entries.

State and persistence: no persistent state. Random ordering is process-local and non-deterministic.

Dependencies and integration: selectable via the `BlockDeletingService` policy configuration. Depends on the template contract and `ContainerData` pending-delete counters through inherited logic.

Risks and test signals: because default shuffle randomness is not injectable, deterministic unit tests should focus on budget accounting through the template or use statistical/containment assertions. Operationally, random selection can reduce hot spots but may delay large pending-delete backlogs compared with top-N ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/RandomContainerDeletionChoosingPolicy.java -->
