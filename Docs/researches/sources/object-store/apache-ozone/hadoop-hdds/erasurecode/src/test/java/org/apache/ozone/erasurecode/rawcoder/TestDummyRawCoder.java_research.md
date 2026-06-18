<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestDummyRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestDummyRawCoder.java

## Purpose
`TestDummyRawCoder` verifies the dummy raw coder framework integration.

## Important APIs, Types, and Functions
It extends `TestRawCoderBase`, configures dummy factories in `setup`, runs two erasure pattern tests, overrides `testCoding(boolean)`, and creates empty chunks with `getEmptyChunks`.

## Control Flow
Setup uses 6 data and 3 parity units. Tests set erased data/parity indexes, run direct and heap variants, and expect dummy outputs to remain empty rather than real reconstructed data.

## State and Persistence Behavior
State is inherited test configuration and per-test chunks.

## Dependencies and Integration Points
It depends on dummy factory/encoder/decoder classes, `ECChunk`, `ByteBuffer`, and JUnit.

## Risks and Test Signals
Risks include dummy behavior being confused with correctness. Signals are no-op output behavior and framework validation around dummy coders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestDummyRawCoder.java -->
