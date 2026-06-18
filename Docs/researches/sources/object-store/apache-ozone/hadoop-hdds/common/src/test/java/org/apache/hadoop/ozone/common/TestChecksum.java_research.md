# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksum.java

## Purpose
Tests Ozone `Checksum` computation and verification for chunk data.

## Important APIs, types, and functions
- Uses `Checksum`, `ChecksumData`, `OzoneChecksumException`, `ContainerProtos.ChecksumType`, and `ByteBuffer`.
- Parameterized helpers cover different checksum types through `getChecksum`, `testVerifyChecksum`, `testIncorrectChecksum`, and `testChecksumMismatchForDifferentChecksumTypes`.

## Control flow
Tests generate random/string data, compute checksum data, verify correct buffers pass, mutate data or checksum type, and assert mismatch exceptions for invalid cases.

## State and persistence behavior
Checksum data represents metadata persisted with chunks, but test state is in memory.

## Dependencies and integration points
Checksum verification protects Ozone container chunk IO and small-file/write paths.

## Risks and test signals
Incorrect checksum verification can accept corrupted data or reject valid data. Tests signal positive verification and mismatch detection across algorithms.
