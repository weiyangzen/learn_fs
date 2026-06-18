<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureEncoder.java

## Purpose
`RawErasureEncoder` is the abstract public base for low-level erasure encoding over ByteBuffers, byte arrays, and `ECChunk` arrays.

## Important APIs, Types, and Functions
It stores `ECReplicationConfig` and exposes `encode(ByteBuffer[], ByteBuffer[])`, `encode(byte[][], byte[][])`, `encode(ECChunk[], ECChunk[])`, abstract `doEncode` overloads, data/parity/all-unit getters, `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

## Control Flow
ByteBuffer encode validates state, returns for zero length, records input positions, dispatches to direct or byte-array implementation, then advances input positions by encoded length. Byte-array encode validates and delegates. `ECChunk` encode unwraps buffers and delegates.

## State and Persistence Behavior
The base owns immutable replication config. Concrete encoders may hold schema-specific tables or native resources.

## Dependencies and Integration Points
It integrates with `EncodingState` subclasses, `ECChunk`, Java/native encoders, and the codec factory layer.

## Risks and Test Signals
Risks include non-synchronized encode despite comments about future thread safety, position advancement surprises, output buffers not being flipped by the framework, and release behavior varying by subclass. Tests cover round trips, direct/heap/sliced buffers, bad shape handling, idempotent release, and position checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureEncoder.java -->
