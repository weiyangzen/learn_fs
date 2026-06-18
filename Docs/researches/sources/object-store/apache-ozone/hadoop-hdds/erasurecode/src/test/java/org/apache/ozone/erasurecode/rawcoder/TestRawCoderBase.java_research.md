<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawCoderBase.java

## Purpose
`TestRawCoderBase` bridges the generic chunk test harness to concrete raw encoder/decoder factories.

## Important APIs, Types, and Functions
It owns encoder/decoder factory classes and instances. Important methods include `testCodingDoMixAndTwice`, `testCodingDoMixed`, `testCoding`, bad input/output tests, `testCodingWithErasingTooMany`, `testIdempotentReleases`, `performTestCoding`, `prepareCoders`, `ensureOnlyLeastRequiredChunks`, `createEncoder`, `createDecoder`, `testInputPosition`, `verifyBufferPositionAtEnd`, and wrapper `encode`/`decode`.

## Control Flow
Tests create coders through reflection, encode parity, prepare erased inputs, decode, compare expected chunks, repeat with direct/heap and sliced/simple buffers, then release coders. Negative paths corrupt inputs/outputs or over-erase to assert exceptions.

## State and Persistence Behavior
Per-test state includes current encoder/decoder objects. Release is called and tested for idempotence.

## Dependencies and Integration Points
It depends on `TestCoderBase`, `RawErasureCoderFactory`, `ECReplicationConfig`, `ECChunk`, AssertJ/JUnit, and concrete factory subclasses.

## Risks and Test Signals
Risks include reflection hiding constructor changes, factory lifecycle state leaking between runs, and native release behavior varying. Passing tests signal round-trip correctness, validation failures, buffer position movement, and release semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawCoderBase.java -->
