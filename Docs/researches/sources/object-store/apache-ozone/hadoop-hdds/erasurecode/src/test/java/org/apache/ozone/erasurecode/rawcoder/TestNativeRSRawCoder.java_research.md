<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeRSRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeRSRawCoder.java

## Purpose
`TestNativeRSRawCoder` runs RS raw coder correctness tests against native ISA-L wrappers when native code is available.

## Important APIs, Types, and Functions
It extends `TestRSRawCoderBase`, configures native RS factories in the constructor, skips tests in `setup` with `Assumptions.assumeTrue(ErasureCodeNative.isNativeCodeLoaded())`, and defines native-specific erasure pattern and after-release tests.

## Control Flow
When native code is present, inherited RS tests run for data/parity erasures, too many erasures, and 10+4 layout. `testAfterRelease63` verifies operations after release fail as expected.

## State and Persistence Behavior
State is inherited per-test raw coder setup. Native resources are created and released during tests.

## Dependencies and Integration Points
It depends on native library loading, native RS factories, and JUnit assumptions.

## Risks and Test Signals
Risks include tests being skipped in many environments and native lifecycle failures only visible on native-enabled hosts. Passing native tests signal Hadoop native accessor compatibility and Ozone wrapper correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeRSRawCoder.java -->
