<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferEncodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferEncodingState.java

## Purpose
`ByteBufferEncodingState` stores per-call encode metadata for ByteBuffer raw encoders.

## Important APIs, Types, and Functions
It extends `EncodingState`, owns `ByteBuffer[] inputs`, `ByteBuffer[] outputs`, and `usingDirectBuffer`, and implements `convertToByteArrayState()` plus `checkBuffers(ByteBuffer[])`.

## Control Flow
Construction uses the first input's remaining length and directness as the contract for all buffers, validates input/output counts, and rejects null, length-mismatched, or mixed directness buffers. Conversion maps heap-backed ByteBuffers to underlying arrays with offsets.

## State and Persistence Behavior
The state is transient per encode call. `RawErasureEncoder` advances input positions after the actual encode, while encoder implementations write outputs using absolute puts.

## Dependencies and Integration Points
It feeds `RSRawEncoder`, `XORRawEncoder`, and native encoder base classes. It integrates with `ByteArrayEncodingState` when heap ByteBuffers need byte-array Java implementations.

## Risks and Test Signals
Risks include non-array heap ByteBuffers failing conversion, direct/heap mixing, and callers expecting outputs to be flipped automatically. Test signals include direct and heap encoding, sliced buffers with non-zero positions, bad count/length failures, and final input positions at end.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferEncodingState.java -->
