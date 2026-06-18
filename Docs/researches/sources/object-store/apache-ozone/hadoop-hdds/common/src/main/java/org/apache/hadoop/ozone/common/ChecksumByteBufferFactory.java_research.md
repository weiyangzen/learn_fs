# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferFactory.java

## Purpose
`ChecksumByteBufferFactory` creates `ChecksumByteBuffer` wrappers for CRC32 and CRC32C, selecting the JDK Java 9+ CRC32C implementation when available and falling back to Hadoop's `PureJavaCrc32C`.

## Important APIs, types, and functions
- `crc32Impl()` returns a `ChecksumByteBufferImpl` around `java.util.zip.CRC32`.
- `crc32CImpl()` tries Java 9 `java.util.zip.CRC32C` when `useJava9Crc32C` is true, logs and disables it on unexpected failure, otherwise returns `PureJavaCrc32C`.
- Nested `Java9Crc32CFactory` uses `MethodHandles.publicLookup` and a constructor `MethodHandle` to instantiate `CRC32C` without requiring Java 9 at compile time.

## Control flow
Class initialization sets `useJava9Crc32C` from `JavaUtils.isJavaVersionAtLeast(9)`. The nested factory resolves the Java 9 constructor only when loaded. `crc32CImpl` attempts JDK CRC32C first and permanently switches the volatile flag off if creation fails.

## State and persistence behavior
The only mutable state is the process-wide volatile `useJava9Crc32C` fallback flag. No persistence exists.

## Dependencies and integration points
It depends on Java method handles, `CRC32`, optional runtime `CRC32C`, Hadoop `PureJavaCrc32C`, `JavaUtils`, and `ChecksumByteBufferImpl`. It is used by `Checksum.Algorithm` for CRC calculations.

## Risks and edge cases
Reflection/method-handle failures are handled differently in static nested initialization versus runtime creation. Once fallback is triggered, the process will continue using pure Java CRC32C. The logger uses `ChecksumByteBufferImpl.class`, which is harmless but slightly misleading.

## Test signals
Tests should verify CRC32 output, CRC32C output on Java 8 and Java 9+ runtimes, fallback after forced Java9 creation failure, direct-buffer support through the returned implementation, and thread visibility of the volatile fallback flag.
