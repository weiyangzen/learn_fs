<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicy.java

Purpose: pluggable policy interface for selecting containers to process during background block deletion.

Important APIs and control flow: `chooseContainerForBlockDeletion` receives a block budget and map of candidate `ContainerData`, and returns `ContainerBlockInfo` values with selected containers and per-container delete counts. `isValidContainerType` defaults to accepting only `KeyValueContainer`.

State and persistence: interface only. Implementations should be stateless or thread-safe because `BlockDeletingService` may run periodically with shared service state.

Dependencies and integration: configured and invoked by `BlockDeletingService`, with default implementations in `TopNOrderedContainerDeletionChoosingPolicy` and `RandomContainerDeletionChoosingPolicy`.

Risks and test signals: custom policies must preserve the meaning of the block budget and avoid returning unsupported container types or zero-delete containers. Tests should cover type filtering, budget exhaustion, empty candidates, and deterministic ordering where required.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/interfaces/ContainerDeletionChoosingPolicy.java -->
