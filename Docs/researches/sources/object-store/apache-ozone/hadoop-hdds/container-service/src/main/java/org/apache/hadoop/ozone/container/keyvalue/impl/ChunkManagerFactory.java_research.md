# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerFactory.java

## Purpose
`ChunkManagerFactory` selects the concrete chunk manager based on persistence, scanner, and sync-write configuration.

## Important APIs, Types, And Functions
The public API is `createChunkManager(ConfigurationSource conf, BlockManager manager, VolumeSet volSet)`. It reads `HDDS_CONTAINER_CHUNK_WRITE_SYNC_KEY`, `HDDS_CONTAINER_PERSISTDATA`, and scanner configuration.

## Control Flow
The factory reads whether writes should sync and whether container data should persist. If persistence is disabled while the scanner is enabled, it warns and forces persistence on. If persistence remains disabled, it returns `ChunkManagerDummyImpl`; otherwise it returns `ChunkManagerDispatcher`.

## State And Persistence
The class has no persistent state. Its decision controls whether chunk data is durable or discarded.

## Dependencies And Integration Points
It depends on Ozone/HDDS config keys, `ContainerScannerConfiguration`, `ChunkManagerDummyImpl`, `ChunkManagerDispatcher`, `BlockManager`, and `VolumeSet`. It is called during `KeyValueHandler` construction.

## Risks And Test Signals
Risks include accidentally enabling non-persistent mode, scanner override surprises, and sync flag propagation mistakes. Tests should cover default persistent selection, non-persistent with scanner disabled, non-persistent with scanner enabled, and sync-write configuration propagation.
