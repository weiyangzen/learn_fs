# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManagerImpl.java

Purpose: Concrete SCM block manager that allocates block IDs in writable containers, owns the deleted-block log and deleting service, and registers metrics/JMX.

Important APIs and types: Implements `BlockManager` and `BlockmanagerMXBean`. Uses `StorageContainerManager`, `PipelineManager`, `WritableContainerFactory`, `SequenceIdGenerator`, `DeletedBlockLogImpl`, `SCMBlockDeletingService`, and deletion metrics.

Control flow: Constructor wires managers, reads container size, registers MBean/metrics, builds `DeletedBlockLogImpl`, and starts service dependencies. `allocateBlock` checks safe mode and size bounds, gets a writable container, and builds an `AllocatedBlock` with a generated local ID and pipeline. `deleteBlocks` groups `DeletedBlock`s by container ID and persists deletion transactions.

State and persistence behavior: Runtime state includes service, metrics, MBean, manager references, and container size. Persistent deletion state is delegated to `DeletedBlockLogImpl`; block IDs use the SCM sequence generator.

Dependencies and integration points: Integrates with SCM HA metadata, container selection, pipeline metrics, logical deletion, JMX, and background block deletion.

Risks: Missing pipeline returns null allocation. Service shutdown happens through both `stop` and `close`, so idempotence matters. Safe-mode checks prevent unsafe mutations.

Test signals: Cover safe-mode exceptions, invalid sizes, successful allocation, missing pipeline, delete grouping, and cleanup of metrics/MBeans/services.
