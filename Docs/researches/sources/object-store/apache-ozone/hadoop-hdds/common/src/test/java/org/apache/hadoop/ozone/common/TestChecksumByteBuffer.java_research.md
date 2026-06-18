# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumByteBuffer.java

## Purpose
Tests checksum factories over heap and direct `ByteBuffer` inputs.

## Important APIs, types, and functions
- Uses Java `Checksum`, `ByteBuffer`, `PureJavaCrc32`, `PureJavaCrc32C`, and Ozone byte-buffer checksum factory helpers.
- Test cases are `testCrc32ByteBufferFactory`, `testCrc32CByteBufferFactory`, and `testWithDirectBuffer`.
- Inner `VerifyChecksumByteBuffer` compares implementations.

## Control flow
The tests feed equivalent data through checksum implementations using byte arrays, heap buffers, and direct buffers, then compare final checksum values.

## State and persistence behavior
State is checksum accumulator state and buffer positions. No persistence.

## Dependencies and integration points
Ozone checksum computation must work for direct buffers used in high-performance IO paths.

## Risks and test signals
A factory that mishandles direct buffers or buffer positions can corrupt checksum validation. These tests signal parity with known Java CRC implementations.
