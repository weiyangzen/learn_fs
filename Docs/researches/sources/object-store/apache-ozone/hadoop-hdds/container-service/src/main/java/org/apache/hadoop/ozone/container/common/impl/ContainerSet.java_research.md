<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerSet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerSet.java

Purpose: concurrent registry of datanode containers, missing-container IDs, recovering containers, metadata-store create info, and on-demand scan routing.

Important APIs and control flow: factory methods build read-only or read-write sets. `addContainer` rejects IDs marked missing unless overwrite is requested, inserts into a `ConcurrentSkipListMap`, persists create info, removes missing state, tracks recovering timeout entries, and registers the container with its volume. `updateContainer` swaps map entries and adjusts volume membership. Removal variants remove fully, memory-only, or mark missing before removal to prevent accidental recreation. `getContainerWithWriteLock` retries when DiskBalancer or other code swaps the container instance during lock acquisition. `getContainerReport` snapshots containers and synchronizes report construction to linearize FCR/ICR. `handleVolumeFailures` marks affected containers missing, logs loss, refreshes a full report, and triggers heartbeat. `buildMissingContainerSetAndValidate` compares Ratis snapshot BCSIDs with loaded containers and marks stale containers unhealthy.

State and persistence: in-memory concurrent maps/sets store live, missing, and recovering IDs. Optional `WitnessedContainerMetadataStore` persists `ContainerCreateInfo` rows and deletes them on full removal. Volume membership is updated on add/update/remove.

Dependencies and integration: central to dispatcher, block deletion, scanners, reports, volume failure handling, and metadata stores.

Risks and test signals: concurrency tests should exercise map swaps while locks are acquired, missing-container recreation prevention, failed-volume iteration while map mutates, report linearization, and BCSID validation. Metadata-store failures surface as `StorageContainerException` and should be tested.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/ContainerSet.java -->
