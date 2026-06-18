# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDispatcher.java

## Purpose
`ChunkManagerDispatcher` is a layout-aware `ChunkManager` facade that routes chunk operations to `FilePerChunkStrategy` or `FilePerBlockStrategy`.

## Important APIs, Types, And Functions
It implements `writeChunk`, `streamInit`, `getStreamDataChannel`, `finishWriteChunks`, `finalizeWriteChunk`, `readChunk`, `deleteChunk`, `deleteChunks`, and `shutdown`. It uses an `EnumMap<ContainerLayoutVersion, ChunkManager>` and private selection helpers.

## Control Flow
Every operation selects the handler from the container's layout version and delegates. `readChunk` additionally verifies non-null data and updates container read statistics. Unsupported layouts produce a `StorageContainerException` with `UNSUPPORTED_REQUEST`.

## State And Persistence
It owns only an in-memory map of strategy instances. Persistence is performed by delegated strategies.

## Dependencies And Integration Points
It depends on layout versions, `FilePerBlockStrategy`, `FilePerChunkStrategy`, `BlockManager`, Ratis `DataChannel`, and container metrics. `ChunkManagerFactory` creates it for persistent data mode, and `KeyValueHandler` uses it for chunk operations.

## Risks And Test Signals
Risks include unsupported layout routing, read-stat double/missing updates, and failure to shut down handlers. Tests should cover both layouts, unsupported layout errors, stream channel routing, read statistics, and shutdown propagation.
