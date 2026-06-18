<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoderBase.java

## Purpose
`TestRSRawCoderBase` defines the shared Reed-Solomon raw coder correctness scenarios.

## Important APIs, Types, and Functions
It extends `TestRawCoderBase` and defines tests for all data erased, selected data erasures, data plus parity erasures, all parity erased, parity subsets, too many erasures, 10+4 layout, and input buffer position.

## Control Flow
Each test sets erased data/parity indexes and calls `testCodingDoMixAndTwice`, negative bad-input tests, or position tests inherited from `TestRawCoderBase`.

## State and Persistence Behavior
State is inherited test configuration adjusted per method.

## Dependencies and Integration Points
It is subclassed by Java and native RS test classes.

## Risks and Test Signals
Risks include duplicated method names/labels and missing randomized erasure combinations beyond fixed scenarios. Passing tests signal RS core correctness for representative patterns and buffer handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoderBase.java -->
