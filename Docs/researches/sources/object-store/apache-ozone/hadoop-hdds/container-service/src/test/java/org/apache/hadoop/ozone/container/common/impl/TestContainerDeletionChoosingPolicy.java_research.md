# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerDeletionChoosingPolicy.java

Purpose: This suite verifies container selection policies used by block deletion: random ordering, top-N ordering by pending delete blocks, and allowed container states for deletion.

Important APIs and types: It uses `BlockDeletingService.chooseContainerForBlockDeletion`, `BlockDeletingService.ContainerBlockInfo`, `RandomContainerDeletionChoosingPolicy`, `TopNOrderedContainerDeletionChoosingPolicy`, `ContainerDeletionChoosingPolicy`, `KeyValueContainerData`, `KeyValueContainer`, and `ContainerLayoutTestInfo.ContainerTest`.

Control flow: Each test configures the policy class, creates a `ContainerSet` via `newContainerSet`, populates `KeyValueContainerData` objects with pending delete counts and states, builds a mocked `OzoneContainer`, and invokes `chooseContainerForBlockDeletion`. The random policy test repeats selection up to 100 times and expects at least one shuffled order. The allowed-state test verifies CLOSED and QUASI_CLOSED are selected but OPEN and CLOSING are not. The top-N test creates containers with random pending counts plus one empty container, checks enough blocks are selected to satisfy a limit, and verifies descending order of pending counts.

State and persistence behavior: No real DB or chunk persistence is used. The state under test is in-memory container metadata: pending deletion block count, container state, and container map membership.

Dependencies and integration points: These policies feed `BlockDeletingService` and therefore control deletion fairness and throughput. The test integrates policy implementations with the service's selection layer and config key `OZONE_SCM_KEY_VALUE_CONTAINER_DELETION_CHOOSING_POLICY`.

Risks: The random test is probabilistic; it fails if two independently shuffled selections match for 100 attempts. Top-N uses random pending counts but derives expected order dynamically. The service object is built with mocked write channel and checksum manager, so only selection is covered.

Test signals: Total selected pending blocks meets or exceeds the limit, random ordering differs at least once, selected IDs include allowed states and exclude disallowed states, empty containers are skipped, and top-N results are non-increasing by pending block count.
