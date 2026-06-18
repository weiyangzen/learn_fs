# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestContainerSizeCountTask.java

Purpose: This test validates `ContainerSizeCountTask` binning of SCM containers by used bytes and lifecycle state into the Recon SQL utilization table `CONTAINER_COUNT_BY_SIZE`.

Important APIs and types: It uses `ContainerSizeCountTask`, `ContainerInfo`, `ContainerID`, `ContainerManager`, `ReconTaskConfig`, `ReconTaskStatusUpdaterManager`, `ReconTaskStatusUpdater`, JOOQ `DSLContext`, `ContainerCountBySizeDao`, `ReconTaskStatusDao`, `UtilizationSchemaDefinition`, and lifecycle constants `OPEN`, `CLOSED`, `CLOSING`, `QUASI_CLOSED`, and `DELETED`.

Control flow: `setUp` obtains the utilization schema DSL and DAO, configures a one-second task interval, mocks task-status updater creation, constructs the task, and truncates the size-count table. `testProcess` feeds mocked container lists through `processContainers`, then mutates the list to add, resize, and remove containers. `testProcessDeletedAndNegativeSizedContainers` sends valid, deleted, and negative-size containers together.

State and persistence behavior: Persistent state is the Recon SQL table keyed by container-size upper bound. The task inserts or updates counts for power-of-two upper-bound bins, keeps rows whose counts drop to zero, and ignores deleted containers for counting. Negative used-byte values are handled as a valid bucket in this test's first scenario but deleted negative-size containers are not counted in the second.

Dependencies and integration points: The suite focuses on the task's internal `processContainers` path rather than polling `ContainerManager`. It verifies JOOQ/DAO persistence used by Recon utilization endpoints and task status wiring through the updater manager.

Risks: The expected DAO row count includes zero-count rows, so changes that physically delete empty bins would require test updates. The test encodes exact bin boundaries such as 512 MB, 2 GB, and 4 GB. It uses mocked `ContainerInfo`, so it does not cover SCM pagination or real manager failure behavior.

Test signals: DAO row counts, exact counts in upper-bound rows, removal of the old 4 GB count after resizing, zero count after removing a 2 GB-bin container, and filtering of `DELETED` containers.
