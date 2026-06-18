## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/BlockManager.java

Purpose: Defines the block-level contract for key-value containers: create/update, read, delete, list, existence, committed length, finalization, read tuning, and shutdown.

Important APIs and functions: `putBlock()` has normal and end-of-block variants. `putBlockForClosedContainer()` persists block data for closed replicas with optional BCSID overwrite. `getBlock()`, `deleteBlock()`, `listBlock()`, `blockExists()`, and `getCommittedBlockLength()` expose block metadata operations. `finalizeBlock()` records finalized blocks. Read configuration getters expose default buffer size, mapped-buffer thresholds, mapped-buffer count, and Netty chunked read mode.

Control flow and state: This is an interface; state is held by implementations and their backing `DatanodeStore`. The API separates block metadata from chunk data while documenting that closed-container import/update expects the caller to update used bytes through chunk writes.

Persistence and dependencies: Integrates `Container`, `BlockData`, `BlockID`, `ChunkInfo`, and `DispatcherContext`. Implementations persist to container RocksDB tables and coordinate with `ChunkManager` for data-file side effects.

Risks: Inconsistent BCSID checks or overwrite behavior can expose stale blocks. `putBlockForClosedContainer()` requires caller-side used-byte accounting, which is easy to miss. Finalized-block state must stay synchronized with container schema support. Read tuning values influence memory mapping and Netty paths.

Test signals: Cover all put/get/delete/list paths, closed-container overwrite and BCSID mismatch behavior, committed length for absent and present blocks, finalization persistence, read-buffer configuration propagation, and shutdown under active operations.
