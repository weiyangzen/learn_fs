<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicyTemplate.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicyTemplate.java

Purpose: template implementation that handles common delete-budget selection while subclasses provide candidate ordering.

Important APIs and control flow: final `chooseContainerForBlockDeletion` null-checks the candidate map, copies values into an ordered list, calls subclass `orderByDescendingPriority`, and iterates until the block budget reaches zero. Each selected container gets `min(remainingBudget, pendingDeletionBlocks)` blocks and is wrapped in `ContainerBlockInfo`. It logs selected containers at debug and aggregate selection at info.

State and persistence: no persistent state. It uses live pending-delete counters from `ContainerData`.

Dependencies and integration: base class for random and top-N policies used by `BlockDeletingService`. Depends on `ContainerUtils.getPendingDeletionBlocks`.

Risks and test signals: if `blockCount` starts at zero or negative, no containers should be selected but the current code still copies/orders candidates; tests should document behavior. Logging message reports original chosen blocks and remaining block count, not original budget in the denominator, which may confuse operators. Subclasses must order in descending priority as expected by the template.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicyTemplate.java -->
