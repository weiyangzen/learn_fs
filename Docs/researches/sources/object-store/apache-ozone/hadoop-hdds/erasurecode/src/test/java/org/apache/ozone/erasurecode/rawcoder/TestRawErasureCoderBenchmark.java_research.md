<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java

## Purpose
`TestRawErasureCoderBenchmark` smoke-tests the benchmark entry point.

## Important APIs, Types, and Functions
It contains `testDummyCoder` and `testRSCoder`, each invoking `RawErasureCoderBenchmark.main` with small arguments.

## Control Flow
The tests run encode/decode benchmark paths for dummy and RS configurations with bounded data sizes so benchmark wiring is covered without long runs.

## State and Persistence Behavior
No persistent state is owned.

## Dependencies and Integration Points
It depends on the benchmark class and JUnit.

## Risks and Test Signals
Risks include timing/memory sensitivity if benchmark defaults change. Passing tests signal CLI argument parsing and basic benchmark execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java -->
