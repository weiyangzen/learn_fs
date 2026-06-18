<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeXORRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeXORRawCoder.java

## Purpose
`TestNativeXORRawCoder` verifies native XOR coder wrapper behavior when native code is available.

## Important APIs, Types, and Functions
It extends `TestXORRawCoderBase`, configures native XOR factories, skips without native code, and defines `testAfterRelease63`.

## Control Flow
Inherited XOR tests exercise direct/heap paths and erasure patterns; the after-release test checks native resources reject later use.

## State and Persistence Behavior
State is inherited per-test coder setup plus native resources.

## Dependencies and Integration Points
It depends on `ErasureCodeNative`, native XOR factories, and JUnit assumptions.

## Risks and Test Signals
Risks include environment-dependent skips and release errors. Passing tests signal native XOR wrapper integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeXORRawCoder.java -->
