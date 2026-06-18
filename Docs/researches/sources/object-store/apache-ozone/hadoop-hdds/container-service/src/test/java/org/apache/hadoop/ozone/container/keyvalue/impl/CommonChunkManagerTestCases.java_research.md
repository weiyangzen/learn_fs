# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/CommonChunkManagerTestCases.java

## Purpose
`CommonChunkManagerTestCases` defines behavior expected of real chunk-manager strategies. It covers invalid write sizes, oversized reads, write/read/delete lifecycle, missing chunks, repeated chunk IO, and finishing writes.

## Important APIs, types, and functions
The class calls `ChunkManager.writeChunk`, `readChunk`, `deleteChunk`, and `finishWriteChunks`, plus `BlockManager.putBlock` for read validation. It uses `WRITE_STAGE`, `COMBINED_STAGE`, `OZONE_SCM_CHUNK_MAX_SIZE`, `StorageContainerException`, `ContainerProtos.Result`, `BlockData`, `ChunkInfo`, and strategy-specific `getLayout().getChunkFile`.

## Control flow
Each test obtains the implementation via `createTestSubject()`. Invalid-length writes set a declared chunk length that does not match the prepared data buffer and expect `INVALID_WRITE_SIZE`. Oversized read manually writes a chunk file larger than `OZONE_SCM_CHUNK_MAX_SIZE`, bypassing the write path, and expects read failure. Normal write/read tests write a chunk, persist block metadata, then read and compare bytes. Multi-write tests create 100 chunk names and offsets and verify aggregate stats.

## State and persistence behavior
The tests assert chunk files are created or deleted on disk, block metadata is inserted before read validation, and volume IO stats match byte totals and operation counts. `finishWriteChunks` uses a mocked `BlockData` with the fixture block ID and then verifies chunk files are closed.

## Dependencies and integration points
These tests are inherited by file-per-block and file-per-chunk strategies, ensuring both strategy-specific implementations satisfy the same container protocol contract. They integrate storage exceptions, layout-specific chunk path generation, and block metadata dependencies for reads.

## Risks and edge cases
Covered risks include accepting mismatched buffer lengths, allowing reads larger than the configured max, partial delete requests being accepted, misreporting missing chunks, leaking temporary files after finish, and cumulative IO-stat drift across repeated writes.

## Test signals
Strong signals are protocol result codes (`INVALID_WRITE_SIZE`, `UNSUPPORTED_REQUEST`, `UNABLE_TO_FIND_CHUNK`), chunk file counts, byte-for-byte buffer comparison, and volume read/write byte/op counters.
