# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerChunkStrategy.java

## Purpose
This suite tests file-per-chunk-specific behavior while inheriting common chunk-manager tests. It focuses on two-stage write/commit handling and compatibility with old chunk files whose physical file length includes the chunk offset.

## Important APIs, types, and functions
The class selects `ContainerLayoutTestInfo.FILE_PER_CHUNK`, uses `ChunkManager.writeChunk` and `deleteChunk`, and references `WRITE_STAGE`, `COMMIT_STAGE`, `ContainerLayoutVersion.FILE_PER_CHUNK.getChunkFile`, `OzoneConsts.CONTAINER_TEMPORARY_CHUNK_PREFIX`, and `ChunkUtils.writeData`.

## Control flow
`testWriteChunkStageWriteAndCommit` writes fixture data in `WRITE_STAGE`, expects a temporary chunk file, then writes the same chunk in `COMMIT_STAGE`, expecting the temp file to be renamed to the final chunk file without an additional IO-stat increment. `deletesChunkFileWithLengthIncludingOffset` manually writes a chunk file at offset 1024 so its file length is `offset + len`, then calls `deleteChunk` with that historical chunk info.

## State and persistence behavior
In file-per-chunk layout, each logical chunk becomes a separate file. During write stage the file is temporary and includes term/index suffixes; during commit it becomes the final chunk name. The compatibility delete test verifies deletion accepts a file whose physical length is larger than the logical chunk length because old clients/datanodes wrote offset-inclusive files.

## Dependencies and integration points
The suite integrates layout-specific chunk naming, temporary-file promotion, Ozone chunk name delimiters, and shared volume IO counters from the abstract fixture. It protects interop behavior between old and new datanode/client versions.

## Risks and edge cases
Risks include leaving temporary files after commit, double-counting commit IO, failing to delete old-format chunk files, or confusing logical chunk length with physical file length.

## Test signals
Signals are final and temporary file existence checks, chunk directory file count, file length assertions, and write IO stats remaining stable across commit.
