# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ChunkManagerDiskWrite.java

## Purpose
Vapor/Freon load generator that writes chunks directly through datanode `ChunkManager` to benchmark local disk/container write paths.

## Important APIs, types, and functions
Command `cmdw`/`chunk-manager-disk-write`, options for chunk size, chunks per block, and container layout. Uses `MutableVolumeSet`, `RoundRobinVolumeChoosingPolicy`, `KeyValueContainer`, `KeyValueContainerData`, `ChunkManagerFactory`, `DispatcherContext`, `BlockID`, `ChunkInfo`, Dropwizard `Timer`, and Freon `runTests`.

## Control flow
`call` initializes Freon, creates one fresh key-value container per worker thread, computes block size, generates random payload data, creates a chunk manager, then runs `writeChunk`. Each operation derives thread id from thread name, selects that thread’s container, computes offset/local block id from thread-local bytes written, builds dispatcher context, wraps the shared data in a `ByteBuffer`, and times `writeChunk`.

## State and persistence behavior
Creates container directories/data on configured datanode volumes and writes chunk files or layout-specific data. Thread-local counters track per-thread block offsets.

## Dependencies and integration points
Exercises datanode storage volume selection, key-value container layout, chunk manager implementation, Freon metrics, and container write-state-machine context.

## Risks and edge cases
Thread id parsing depends on pool thread naming. Random container IDs can collide rarely. Shared byte array is safe, but per-operation `ByteBuffer.wrap` is needed for independent position. Containers are not explicitly cleaned.

## Test signals
No direct tests. Runtime signals are Freon operation counts, `chunk-write` timer, and absence of `StorageContainerException`.
