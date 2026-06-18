# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/checksum/TestReplicatedBlockChecksumComputer.java

## Purpose
`TestReplicatedBlockChecksumComputer` verifies block-level checksum combination for replicated blocks in MD5-of-CRC mode and composite CRC mode.

## Important APIs, Types, And Functions
`testComputeMd5Crc` creates random chunk checksum bytes, computes the expected `MD5Hash.digest`, runs `ReplicatedBlockChecksumComputer.compute(MD5MD5CRC)`, and asserts output bytes. `testComputeCompositeCrc` uses `CrcComposer` to compute expected composite CRC32C output, runs `compute(COMPOSITE_CRC)`, and asserts output bytes. `buildBlockChecksumComputer` creates a single `ChunkInfo` with `ChecksumData` and returns a `ReplicatedBlockChecksumComputer`.

## Control Flow
Each test builds deterministic expected output from the same random checksum input, constructs a one-chunk block checksum computer, calls `compute`, and compares the resulting output buffer.

## State And Persistence Behavior
No persistent state is used. All data is local to the test method.

## Dependencies And Integration Points
It depends on `ReplicatedBlockChecksumComputer`, `AbstractBlockChecksumComputer`, `CrcComposer`, `CrcUtil`, Hadoop `MD5Hash` and `DataChecksum`, protobuf `ByteString`, and datanode checksum protobufs.

## Risks And Edge Cases
The tests cover a single chunk only. Multi-chunk composition, mixed checksum types, and invalid checksum lengths are not covered here. Random input is secure-random, but expected and actual derive from the same bytes, so the tests should remain deterministic in outcome.

## Test Signals
Validates the two primary replicated block checksum combine modes at the unit level.
