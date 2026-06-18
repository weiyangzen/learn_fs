<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureDecoder.java

## Purpose
`RawErasureDecoder` is the abstract public base for low-level decode operations over ByteBuffers, byte arrays, and `ECChunk` arrays.

## Important APIs, Types, and Functions
It stores `ECReplicationConfig` and exposes synchronized `decode(ByteBuffer[], int[], ByteBuffer[])`, synchronized `decode(byte[][], int[], byte[][])`, synchronized `decode(ECChunk[], int[], ECChunk[])`, abstract `doDecode` methods, data/parity count getters, `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

## Control Flow
Public decode constructs a state object, returns immediately for zero length, records input positions for ByteBuffers, dispatches to direct or byte-array implementation, then advances non-null input positions by the decode length. The `ECChunk` overload unwraps chunks through `CoderUtil.toBuffers`.

## State and Persistence Behavior
The base stores immutable replication config. Decode methods are synchronized, protecting mutable concrete decoder state such as RS cached matrices.

## Dependencies and Integration Points
It integrates with state classes, `ECChunk`, `CoderUtil`, Java/native concrete decoders, and all raw coder tests.

## Risks and Test Signals
Risks include serialized decode throughput, position advancement surprises, invalid erased indexes not fully checked in the base, and release semantics being left to subclasses. Tests cover bad inputs/outputs, too many erasures, positions at end, idempotent releases, and decode after release for native wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureDecoder.java -->
