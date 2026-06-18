<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoder.java

## Purpose
`TestXORRawCoder` runs the shared XOR suite against pure-Java XOR coders.

## Important APIs, Types, and Functions
It extends `TestXORRawCoderBase` and supplies `XORRawErasureCoderFactory` for both encoder and decoder.

## Control Flow
All tests are inherited from the XOR base class.

## State and Persistence Behavior
Per-test Java XOR coders are created and released by the base.

## Dependencies and Integration Points
It depends on Java XOR factory classes and inherited raw coder tests.

## Risks and Test Signals
Passing tests signal Java XOR correctness for representative erasures and validation failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoder.java -->
