<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCoderBase.java

## Purpose
`TestCoderBase` is the shared high-level test harness for erasure coder data generation, chunk allocation, erasure simulation, verification, and diagnostics.

## Important APIs, Types, and Functions
Important fields configure data/parity counts, chunk size, erased data/parity indexes, direct vs heap, fixed data, allocator, and zero chunks. Key methods include `prepare`, `prepareBufferAllocator`, `compareAndVerify`, `getErasedIndexesForDecoding`, `prepareInputChunksForDecoding`, `backupAndEraseChunks`, `eraseDataFromChunks`, mark/restore helpers, clone helpers, output allocation, data/parity preparation, `toArrays`, `dumpSetting`, `dumpChunks`, and `corruptSomeChunk`.

## Control Flow
Tests call `prepare`, allocate data chunks, encode parity, clone expected erased chunks, null out erased positions, prepare decode inputs/outputs, run coder operations, and compare decoded chunks with backups. Data may be fixed deterministic or random.

## State and Persistence Behavior
State is per test instance and includes generated fixed data and allocator mode. There is no persistence outside test memory.

## Dependencies and Integration Points
It depends on `ECChunk`, `BufferAllocator`, `OzoneConfiguration`, random utilities, and JUnit assertions. `TestRawCoderBase` builds on it for raw coder-specific execution.

## Risks and Test Signals
Risks include tests hiding bugs through deterministic data, mark/reset assumptions on ByteBuffers, and direct/heap mode not being reset between tests. Strong signals are successful direct/heap/sliced tests, compare failures pinpointing decode corruption, and position verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCoderBase.java -->
