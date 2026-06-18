# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestBlockManagerImpl.java

## Purpose
This suite tests `BlockManagerImpl` block metadata persistence, BCSID handling, list behavior, closed-container put-block semantics, and incremental chunk-list merging for hsync-style writes.

## Important APIs, types, and functions
The tests use `BlockManagerImpl.putBlock`, `putBlockForClosedContainer`, `getBlock`, and `listBlock`, plus `BlockUtils.getDB` to inspect RocksDB metadata. Test data is built with `BlockData`, `BlockID`, `ChunkInfo`, `INCREMENTAL_CHUNK_LIST`, and `BlockManagerImpl.FULL_CHUNK`. Layout/schema coverage is provided by `ContainerTestVersionInfo.ContainerTest`.

## Control flow
`initTest` selects layout/schema, initializes an `HddsVolume`, creates a `KeyValueContainer`, and prepares two block records. Basic tests put blocks with and without BCSID, read them back, and list them. Closed-container tests close the container, then put blocks with different BCSID values and overwrite flags while inspecting in-memory and persisted metadata. Flush tests simulate repeated hsyncs that either extend a partial chunk or merge full chunks with a trailing incremental chunk.

## State and persistence behavior
The suite verifies `blockCount`, `blockCommitSequenceId`, block table rows, metadata table keys for block count and BCSID, and bytes-used metadata. It specifically asserts that `putBlockForClosedContainer` can persist blocks with higher BCSID without making them readable until container BCSID is overwritten, and that simple put-block operations without corresponding write-chunk calls do not alter persisted bytes used.

## Dependencies and integration points
The tests integrate key-value container creation, schema-aware DB stores, block metadata encoding, chunk metadata lists, schema-v1 assumptions, and cache shutdown via `BlockUtils.shutdownCache`. They are central for datanode recovery and hsync semantics.

## Risks and edge cases
Risks include double-counting blocks on overwrite, decreasing container BCSID, exposing blocks whose BCSID is newer than the container, losing full chunk markers during incremental merge, and updating bytes-used from block metadata alone.

## Test signals
Signals include exact block count/BCSID values in both `KeyValueContainerData` and RocksDB metadata, `StorageContainerException` on reads gated by BCSID, chunk list lengths/offsets/lengths after flush merges, and schema-v1 skip assumptions for incremental-list behavior.
