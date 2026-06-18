<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCodecRawCoderMapping.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCodecRawCoderMapping.java

## Purpose
`TestCodecRawCoderMapping` verifies that `CodecUtil` creates the expected raw coder type for RS and XOR configurations.

## Important APIs, Types, and Functions
It has `testRSDefaultRawCoder` and `testXORRawCoder`, using `ECReplicationConfig`, `CodecUtil.createRawEncoderWithFallback`, and `createRawDecoderWithFallback`.

## Control Flow
Each test creates a config string, asks `CodecUtil` for encoder/decoder, and asserts native types when native code is loaded or Java fallback types otherwise.

## State and Persistence Behavior
No persistent state is owned.

## Dependencies and Integration Points
It depends on native availability via `ErasureCodeNative`, factory registry ordering, and JUnit assertions.

## Risks and Test Signals
Risks include environment-dependent assertions if native availability changes mid-JVM and registry order drift. Passing tests signal correct fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCodecRawCoderMapping.java -->
