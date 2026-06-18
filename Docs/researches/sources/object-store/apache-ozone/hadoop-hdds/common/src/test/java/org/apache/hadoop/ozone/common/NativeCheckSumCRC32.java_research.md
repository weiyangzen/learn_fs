# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/NativeCheckSumCRC32.java

## Purpose
Provides a test checksum adapter around Hadoop native CRC32 support for comparing checksum implementations.

## Important APIs, types, and functions
- Implements Java `Checksum`-style methods `update(int)`, `update(byte[], int, int)`, `getValue`, and `reset`.
- Uses `NativeCRC32Wrapper` for native CRC operations and throws `NotImplementedException` for unsupported update shapes where applicable.
- Supports `ByteBuffer`-oriented native checksum comparison in tests.

## Control flow
The adapter forwards supported update calls to the native wrapper, returns the native checksum value, and resets native state when requested.

## State and persistence behavior
State is native checksum accumulator state. No persistence.

## Dependencies and integration points
Used by checksum comparison tests to ensure Ozone checksum code matches native Hadoop implementations.

## Risks and test signals
Native checksum availability and API limitations can affect tests. The adapter isolates native behavior for cross-implementation validation.
