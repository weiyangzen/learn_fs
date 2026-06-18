<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayEncodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayEncodingState.java

## Purpose
`ByteArrayEncodingState` stores per-call encode metadata for heap-array raw encoders.

## Important APIs, Types, and Functions
It extends `EncodingState`, owns input/output arrays plus input/output offsets, and implements `convertToByteBufferState()` and `checkBuffers(byte[][])`. The public constructor uses the first input's length as `encodeLength` and initializes offsets to zero.

## Control Flow
Construction validates data/parity buffer counts and equal lengths. Conversion clones every input array range into a direct ByteBuffer and allocates direct output buffers for native encoders.

## State and Persistence Behavior
All state is transient per encode call. Encoder implementations mutate caller output arrays and may read from caller input arrays.

## Dependencies and Integration Points
It is created by `RawErasureEncoder.encode(byte[][], byte[][])` and by `ByteBufferEncodingState.convertToByteArrayState()` for heap-backed ByteBuffers.

## Risks and Test Signals
Risks include `null` inputs being rejected for encode, full-array length assumptions, and output offsets only being honored by conversion/internal constructors. Tests should cover bad counts, length mismatches, heap ByteBuffer offset conversions, and native heap-array fallback.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayEncodingState.java -->
