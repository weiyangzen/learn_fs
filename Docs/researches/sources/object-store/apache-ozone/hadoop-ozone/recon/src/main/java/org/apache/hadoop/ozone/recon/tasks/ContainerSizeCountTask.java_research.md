# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerSizeCountTask.java

Purpose: Periodic SCM-side task that bins containers by used-byte size and stores counts in the SQL `CONTAINER_COUNT_BY_SIZE` table.

Important APIs: `run`, `runTask`, test-visible `processContainers`, private `process`, `writeCountsToDB`, delete handling, and static bin-key helpers.

Control flow and persistence: `run` waits for the configured interval while `canRun`, then invokes `initializeAndRunTask`. `runTask` gets all containers from `ContainerManager`, truncates SQL counts on first run, and calls `processContainers`. The task keeps an in-memory `processedContainers` map of container ID to last size. Each pass increments counts for new/current containers, decrements previous bins on size change, ignores containers already marked `DELETED`, and decrements counts for containers missing from the latest SCM list.

Dependencies and integration: uses SCM `ContainerManager`, JOOQ DSL, generated `ContainerCountBySizeDao`, `ReconUtils.getContainerSizeUpperBound`, and `ReconTaskStatusUpdater`.

Risks: state is partly in memory; restart truncates and rebuilds from current SCM list. Negative used bytes are normalized to zero. SQL updates are read-modify-write per bin and can preserve zero/negative rows if inputs are inconsistent. The write lock protects local state but not other SQL writers.

Test signals: cover first-run truncation, deleted-container removal, size updates across bins, negative used bytes, task status update on partial failures, and SQL insert/update behavior.
