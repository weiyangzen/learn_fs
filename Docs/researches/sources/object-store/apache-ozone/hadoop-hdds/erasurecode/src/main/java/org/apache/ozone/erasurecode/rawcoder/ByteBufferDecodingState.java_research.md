<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferDecodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferDecodingState.java

## Purpose
`ByteBufferDecodingState` is the per-call decode state for ByteBuffer inputs and outputs.

## Important APIs, Types, and Functions
It extends `DecodingState` and records `ByteBuffer[] inputs`, `ByteBuffer[] outputs`, `int[] erasedIndexes`, `decodeLength`, and `usingDirectBuffer`. It implements `convertToByteArrayState()`, `checkInputBuffers(ByteBuffer[])`, and `checkOutputBuffers(ByteBuffer[])`.

## Control Flow
The constructor finds the first non-null input, adopts its remaining bytes as decode length and direct/heap mode, validates parameter counts, checks all non-null inputs for identical remaining length and directness, and requires all outputs to be non-null with matching length/directness. Conversion exposes heap-backed arrays with `arrayOffset() + position()` offsets.

## State and Persistence Behavior
State exists for one decode call. The top-level decoder advances non-null input positions after decoding; state methods themselves mostly use absolute reads and offset metadata.

## Dependencies and Integration Points
It is instantiated by `RawErasureDecoder.decode(ByteBuffer[], int[], ByteBuffer[])` and feeds Java and native decoder implementations. Heap conversion assumes buffers are array-backed.

## Risks and Test Signals
Risks include mixing direct and heap buffers, using read-only or non-array heap buffers with conversion, too few valid inputs, and output count mismatch with erased indexes. Tests should include direct/heap parity, sliced buffers, position advancement, redundant null inputs, and invalid buffer shapes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferDecodingState.java -->
