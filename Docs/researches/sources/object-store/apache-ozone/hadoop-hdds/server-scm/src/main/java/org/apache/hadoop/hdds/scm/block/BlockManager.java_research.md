# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/BlockManager.java

Purpose: SCM-facing interface for block allocation, logical deletion, lifecycle management, and access to the block deletion subsystem.

Important APIs and types: Defines `allocateBlock`, `deleteBlocks`, `getDeletedBlockLog`, `start`, `stop`, `getSCMBlockDeletingService`, and inherited `close`. Uses `ReplicationConfig`, `ExcludeList`, `AllocatedBlock`, and `BlockGroup`.

Control flow: Implementations allocate blocks inside containers and persist logical deletion requests into `DeletedBlockLog` atomically.

State and persistence behavior: Stateless interface. The contract requires deletion transactions to be persisted before deletion is considered accepted.

Dependencies and integration points: Called by SCM block protocol paths and integrated with container allocation and asynchronous physical block deletion.

Risks: Delete atomicity is crucial for OM/SCM consistency. Allocation may fail from safe mode, capacity, pipeline, or timeout issues in implementations.

Test signals: Implementation tests should cover allocation validation, safe-mode rejection, deletion transaction persistence, and lifecycle methods.
