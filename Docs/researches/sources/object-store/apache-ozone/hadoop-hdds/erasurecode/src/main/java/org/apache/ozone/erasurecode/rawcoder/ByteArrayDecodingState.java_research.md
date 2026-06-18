<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayDecodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayDecodingState.java

## Purpose
`ByteArrayDecodingState` stores all per-call decode metadata for byte-array based raw decoders.

## Important APIs, Types, and Functions
It extends `DecodingState` and owns `byte[][] inputs`, `int[] inputOffsets`, `int[] erasedIndexes`, `byte[][] outputs`, and `int[] outputOffsets`. Constructors either validate caller arrays and initialize zero offsets or accept precomputed offsets from a ByteBuffer conversion. Key methods are `convertToByteBufferState()`, `checkInputBuffers(byte[][])`, and `checkOutputBuffers(byte[][])`.

## Control Flow
Construction finds the first non-null input to define `decodeLength`, validates counts and erased/output shape through `DecodingState`, then enforces equal input/output lengths. Conversion clones non-null inputs into direct buffers and allocates direct outputs for native-friendly decoding.

## State and Persistence Behavior
The state is per decode call and not retained beyond the caller's stack except during method execution. Output arrays are caller-owned and mutated by decoders.

## Dependencies and Integration Points
It depends on `CoderUtil.cloneAsDirectByteBuffer` and `ByteBufferDecodingState`. It is used by `RawErasureDecoder` heap-array decode and by native decoders converting heap arrays to direct buffers.

## Risks and Test Signals
Risks include assuming full array length instead of logical offsets in public constructors, insufficient valid inputs, and output length mismatch. Tests should cover erased/null inputs, redundant null inputs, too few valid inputs, mismatched lengths, and heap-to-direct native conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayDecodingState.java -->
