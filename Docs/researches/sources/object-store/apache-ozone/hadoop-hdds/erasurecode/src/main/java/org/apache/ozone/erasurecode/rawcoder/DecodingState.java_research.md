<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DecodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DecodingState.java

## Purpose
`DecodingState` is the shared base for decode state validation across byte-array and ByteBuffer decoders.

## Important APIs, Types, and Functions
It stores `RawErasureDecoder decoder` and `int decodeLength`. Its `checkParameters(T[] inputs, int[] erasedIndexes, T[] outputs)` validates total input count, erased output count, and maximum erasures.

## Control Flow
Validation checks that `inputs.length` equals data plus parity units, `erasedIndexes.length` equals `outputs.length`, and erasures do not exceed parity units.

## State and Persistence Behavior
No persistent state exists. Subclasses fill fields for one decode invocation.

## Dependencies and Integration Points
It is used by `ByteArrayDecodingState` and `ByteBufferDecodingState`, and its rules are relied on by `RawErasureDecoder` before concrete coders run.

## Risks and Test Signals
Risks are incomplete validation: erased index bounds and duplicate indexes are not checked here. Test signals include bad input count, too many erasures, output count mismatches, and invalid erased indexes surfaced by concrete coders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DecodingState.java -->
