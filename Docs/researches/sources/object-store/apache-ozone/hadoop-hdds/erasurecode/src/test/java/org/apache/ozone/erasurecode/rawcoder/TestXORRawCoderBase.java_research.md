<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoderBase.java

## Purpose
`TestXORRawCoderBase` defines shared XOR raw coder correctness and negative scenarios.

## Important APIs, Types, and Functions
It extends `TestRawCoderBase` and defines tests for erasing data unit 0, parity 0, data unit 5, too many erasures, and a bad-input data erasure.

## Control Flow
Each test sets the appropriate erased indexes and calls inherited round-trip or bad-input routines.

## State and Persistence Behavior
State is inherited and adjusted per test method.

## Dependencies and Integration Points
It is subclassed by Java and native XOR test classes.

## Risks and Test Signals
Risks include XOR-specific one-parity assumptions and limited erasure combinations. Passing tests signal XOR encode/decode and validation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoderBase.java -->
