# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumImplsComputeSameValues.java

## Purpose
Compares multiple CRC32 and CRC32C implementations to ensure they compute identical values.

## Important APIs, types, and functions
- Uses Java `CRC32`, Hadoop `PureJavaCrc32`, `PureJavaCrc32C`, `NativeCRC32Wrapper`, and `NativeCheckSumCRC32`.
- Test cases are `testCRC32ImplsMatch`, `testCRC32CImplsMatch`, and helper `validateImpls`.

## Control flow
The tests generate random data, feed the same buffers through each implementation, and assert all reported checksum values match.

## State and persistence behavior
Only checksum accumulators and random test buffers are used. No persistence.

## Dependencies and integration points
Ozone may use native or pure-Java checksum implementations depending on platform/runtime. Parity is essential for data integrity.

## Risks and test signals
Platform-specific checksum drift would cause false corruption reports or missed corruption. These tests signal implementation equivalence.
