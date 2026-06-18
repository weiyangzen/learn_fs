# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/utils/BufferUtils.java

## Purpose

`BufferUtils` centralizes common ByteBuffer and ByteString helper operations for Ozone chunk IO. It handles buffer allocation, read-only views, length calculations, concatenation, bin counts, and complete gathering-channel writes.

## APIs and control flow

`assignByteBuffers(totalLen, bufferCapacity)` allocates an array sized by `getNumberOfBins`, using full-size buffers except the last. `getReadOnlyByteBuffers` adapts `ByteString` lists or `ByteBuffer[]` into read-only buffers. `concatByteStrings` concatenates a list in order. `getBuffersLen` sums sizes. `getNumberOfBins` implements ceiling division with overflow detection. The three `writeFully` overloads loop until each buffer's remaining bytes are written, throwing if a channel reports a negative write.

## State, dependencies, and integration

The class is stateless and depends on Guava preconditions, Ratis `ByteString`, `GatheringByteChannel`, and SLF4J. It is used by all `ChunkBuffer` implementations for reliable writes.

## Risks and test signals

`writeFully` can spin on a non-blocking channel returning zero repeatedly; callers should use appropriate channel types. `concatByteStrings` can be costly for many components. Tests should cover zero/negative argument rejection, exact last-buffer sizing, integer overflow, read-only protection, and partial-write channels.
