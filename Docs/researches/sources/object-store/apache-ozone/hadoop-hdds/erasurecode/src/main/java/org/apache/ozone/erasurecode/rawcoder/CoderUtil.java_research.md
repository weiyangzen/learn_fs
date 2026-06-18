<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/CoderUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/CoderUtil.java

## Purpose
`CoderUtil` contains package-private helper routines shared by raw coder implementations and state converters.

## Important APIs, Types, and Functions
Important helpers include `getEmptyChunk(int)`, `resetBuffer(ByteBuffer,int)`, `resetBuffer(byte[],int,int)`, `resetOutputBuffers(...)`, `toBuffers(ECChunk[])`, `cloneAsDirectByteBuffer(byte[],int,int)`, `findFirstValidInput(T[])`, and `getValidIndexes(T[])`. It owns a grow-only static zero-filled `emptyChunk` cache.

## Control Flow
Output reset methods copy zeros from the cached empty chunk. `getEmptyChunk` returns the existing cache if large enough, otherwise synchronizes and grows it with a second length check. `toBuffers` unwraps chunks and zeroes buffers marked `allZero`. Conversion helpers allocate direct buffers and copy source data.

## State and Persistence Behavior
The only persistent state is the process-local static `emptyChunk` array. It is intentionally reused and can grow but should not shrink.

## Dependencies and Integration Points
It integrates with all raw coders, `ECChunk`, and state conversion classes. The tests include a concurrency-focused check that the zero cache does not shrink when requests race.

## Risks and Test Signals
Risks include exposing a shared mutable zero array inside the package, concurrency regressions in cache growth, position changes while zeroing ByteBuffers, and failing to honor `ECChunk.allZero`. Test signals are `TestCoderUtil`, raw coder output reset behavior, all-zero chunk decoding, and concurrent calls to `getEmptyChunk`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/CoderUtil.java -->
