<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawDecoder.java

## Purpose
`RSRawDecoder` is the pure-Java Reed-Solomon decoder fallback compatible with ISA-L matrix behavior.

## Important APIs, Types, and Functions
It extends `RawErasureDecoder`, owns `encodeMatrix`, per-erasure `decodeMatrix`, `invertMatrix`, `gfTables`, `cachedErasedIndexes`, `validIndexes`, `numErasedDataUnits`, and `erasureFlags`. Important methods are both `doDecode` overloads, `prepareDecoding`, `processErasures`, and `generateDecodeMatrix`.

## Control Flow
Construction builds a Cauchy encode matrix and rejects data+parity counts at or above GF(256) field size. Each decode resets outputs, prepares decoding tables if erased/valid indexes changed, selects the first `k` valid inputs, and calls `RSUtil.encodeData` with decode tables. Decode matrix generation removes erased rows, inverts the surviving data matrix, copies rows for erased data units, and computes parity recovery rows from the encode matrix.

## State and Persistence Behavior
The encode matrix persists for the decoder lifetime. Decode matrices and GF tables are cached for the most recent erased/valid index pattern and reused on identical patterns. No disk persistence exists.

## Dependencies and Integration Points
It depends on `GF256`, `RSUtil`, `DumpUtil`, and the validation in `RawErasureDecoder`/state classes. It is selected by `RSRawErasureCoderFactory` and used when native RS is unavailable.

## Risks and Test Signals
Risks include mutable cached decode state in a synchronized decoder, invalid erased indexes, GF matrix inversion failures, and compatibility drift with ISA-L. Tests cover many 6+3 and 10+4 erasure patterns, too many erasures, input position behavior, direct and heap buffers, and native-vs-Java fallback mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawDecoder.java -->
