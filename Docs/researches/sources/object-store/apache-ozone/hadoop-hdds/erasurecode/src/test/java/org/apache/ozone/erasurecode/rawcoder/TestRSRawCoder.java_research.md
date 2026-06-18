<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoder.java

## Purpose
`TestRSRawCoder` runs the shared RS correctness suite against pure-Java RS coders.

## Important APIs, Types, and Functions
It extends `TestRSRawCoderBase`, supplies `RSRawErasureCoderFactory` for encoder and decoder, and disables verbose dumps in setup.

## Control Flow
All meaningful test flow is inherited from `TestRSRawCoderBase` and `TestRawCoderBase`.

## State and Persistence Behavior
Per-test Java coder instances hold RS matrices/tables; no persistence exists.

## Dependencies and Integration Points
It depends on Java RS factory classes and inherited JUnit tests.

## Risks and Test Signals
Passing tests are the main signal that Java fallback remains correct across data/parity erasure patterns and buffer modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoder.java -->
