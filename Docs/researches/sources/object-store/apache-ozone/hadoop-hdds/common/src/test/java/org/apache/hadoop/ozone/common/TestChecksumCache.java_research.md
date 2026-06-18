# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumCache.java

## Purpose
Tests checksum caching/reuse behavior for Ozone checksum algorithms.

## Important APIs, types, and functions
- Uses `Checksum`, `Checksum.Algorithm`, `ContainerProtos.ChecksumType`, `ByteString`, and `ByteBuffer`.
- Parameterized tests iterate over checksum types/algorithms and functions that compute checksum bytes.

## Control flow
For each algorithm, tests compute checksum data for buffers and compare outputs across cached/reused checksum instances or computation paths.

## State and persistence behavior
State is in-memory checksum object cache and generated checksum bytes. No persistence.

## Dependencies and integration points
Checksum caching affects hot chunk IO paths by reducing object allocation while preserving correctness.

## Risks and test signals
Reusing checksum instances without reset can produce wrong values. Tests signal cache correctness across algorithms.
