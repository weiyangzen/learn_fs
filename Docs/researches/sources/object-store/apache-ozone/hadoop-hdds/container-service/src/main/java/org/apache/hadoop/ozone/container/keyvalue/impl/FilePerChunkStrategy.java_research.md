# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerChunkStrategy.java

## Purpose
`FilePerChunkStrategy` implements `ChunkManager` for FILE_PER_CHUNK containers, storing each chunk in a separate file with Ratis temp-file staging and commit semantics.

## Important APIs, Types, And Functions
Main methods are `writeChunk`, `readChunk`, `deleteChunk`, and `deleteChunks`; helpers are `getChunkFile`, `getTmpChunkFile`, and `commitChunk`. Constructor state includes sync mode, `BlockManager`, read buffer/mmap settings, mapped-buffer manager, and Netty read toggle.

## Control Flow
`WRITE_DATA` writes payload to a term/log-index temporary file and does not update committed stats. `COMMIT_DATA` renames the temp file to the final chunk file unless final already exists from replay, then updates stats. `COMBINED` writes directly to final and updates stats. Reads consider final, temp, then final again when the dispatcher allows tmp reads, and use block metadata to translate nonzero chunk offsets. Deletes remove whole chunk files only when length checks prove the request covers the stored file.

## State And Persistence
It persists one file per chunk plus temporary staging files. Block metadata is persisted separately by `BlockManager`; chunk stats are updated only on commit/combined writes.

## Dependencies And Integration Points
Dependencies include `ChunkUtils`, `FILE_PER_CHUNK` layout helpers, `BlockManager`, `DispatcherContext`, Ozone temp chunk naming constants, Hadoop `FileUtil`, and container/chunk types. It remains available for old containers/tests even though handler construction warns against configured FILE_PER_CHUNK layout.

## Risks And Test Signals
Risks include temp-file leftovers, final-file idempotency without checksum comparison, partial-read offset errors, unsupported shared-file delete cases, and low coverage for deprecated layout. Tests should cover staged write/commit, replay with existing final file, temp read fallback, combined writes, nonzero-offset reads, delete length validation, missing chunks, and mmap/Netty reads.
