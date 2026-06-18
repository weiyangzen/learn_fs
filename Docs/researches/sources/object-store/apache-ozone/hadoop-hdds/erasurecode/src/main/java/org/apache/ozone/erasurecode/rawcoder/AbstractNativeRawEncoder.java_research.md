<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawEncoder.java

## Purpose
`AbstractNativeRawEncoder` is the shared base for native raw encoders. It converts Ozone encode state into native-accessor arguments and protects native encoder state with a read/write lock.

## Important APIs, Types, and Functions
The class extends `RawErasureEncoder`, owns protected `ReentrantReadWriteLock encoderLock`, implements `doEncode(ByteBufferEncodingState)` and `doEncode(ByteArrayEncodingState)`, declares `performEncodeImpl(ByteBuffer[], int[], int, ByteBuffer[], int[])`, and prefers direct buffers.

## Control Flow
The direct path records input and output positions, locks `encoderLock.readLock()`, invokes the subclass native implementation, and unlocks. The byte-array path logs a performance advisory, clones heap arrays to direct buffers, encodes through the direct path, and copies each direct output back into its caller-provided output array.

## State and Persistence Behavior
Only lock state is owned by the base class. Native resources live in concrete Hadoop native encoder wrappers and are released by subclasses.

## Dependencies and Integration Points
It integrates with `NativeRSRawEncoder`, `NativeXORRawEncoder`, `ByteBufferEncodingState`, `ByteArrayEncodingState`, and Hadoop native ISA-L accessors through subclass hooks.

## Risks and Test Signals
The main risks are native lifecycle races, missing output copy-back, and performance surprises when heap arrays silently allocate direct buffers. Test signals include native RS/XOR parity correctness, direct and heap paths, sliced buffers, release idempotence, and fallback to Java coders when native construction fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawEncoder.java -->
