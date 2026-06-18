# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDummyImpl.java

## Purpose
`ChunkManagerDummyImpl` is a non-persistent chunk manager for performance/testing configurations. It discards writes and returns zero-filled buffers for reads.

## Important APIs, Types, And Functions
It implements `writeChunk`, `readChunk`, `deleteChunk`, and `deleteChunks`. Static `newMappedByteBuffer` creates a read-only zero-filled `MappedByteBuffer` sized to `OZONE_SCM_CHUNK_MAX_SIZE`.

## Control Flow
Construction creates a temporary mapped zero file. `writeChunk` validates write-stage buffer length and increments volume IO stats, then updates container write stats during commit stage. `readChunk` duplicates the zero buffer, limits it to requested length after `limitReadSize`, and wraps it as `ChunkBuffer`. Deletes are no-ops.

## State And Persistence
No container data is persisted. Only a temporary zero backing file exists, and stats are updated to emulate IO.

## Dependencies And Integration Points
It depends on Java NIO mapping, `ChunkUtils`, `ContainerData`, `HddsVolume`, `VolumeIOStats`, and `DispatcherContext`. It is selected by `ChunkManagerFactory` only when persistence is disabled and scanner settings allow it.

## Risks And Test Signals
Risks include accidental production use, scanner incompatibility, oversize reads, and misleading success while data is discarded. Tests should verify factory selection, write/commit accounting, zero-read content, oversize read rejection, and no-op deletes.
