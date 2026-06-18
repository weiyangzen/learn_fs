# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/util/NativeCRC32Wrapper.java

## Purpose
Test-scope adapter that exposes Hadoop common's package-private `NativeCrc32` to Ozone benchmarks so native CRC32 and CRC32C implementations can be compared with Ozone checksum code.

## Important APIs, Types, And Functions
Constants `CHECKSUM_CRC32` and `CHECKSUM_CRC32C`, availability check `isAvailable()`, ByteBuffer and byte-array verification helpers, and ByteBuffer and byte-array calculation helpers. All public methods are thin static delegates.

## Control Flow
Callers check native-library availability, then pass checksum buffers, data buffers, offsets, lengths, file name, and base position through unchanged to `NativeCrc32`. Verification may throw `ChecksumException`; calculation mutates the supplied sums buffer or array.

## State And Persistence
The wrapper has no persistent state and cannot be instantiated. State is entirely in caller-owned buffers and Hadoop native CRC library availability.

## Dependencies And Integration Points
Integrates with Hadoop `org.apache.hadoop.util.NativeCrc32`, `java.nio.ByteBuffer`, and Hadoop `ChecksumException`. It exists in the same package to cross the package-private boundary.

## Risks
Because this is only a wrapper, risks are API drift in Hadoop's package-private class, incorrect buffer positions/offsets supplied by benchmarks, and accidentally depending on this test helper from production code.

## Test Signals
Benchmark and test signals are native CRC availability detection, matching CRC32/CRC32C results for ByteBuffer and byte-array paths, and expected `ChecksumException` behavior for corrupted data.
