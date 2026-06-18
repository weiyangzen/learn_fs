# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ClientId.java

## Purpose
Generates and converts UUID-based 16-byte IPC client IDs.

## Important APIs, Types, And Functions
Constants are `BYTE_LENGTH = 16` and `shiftWidth = 8`. APIs are `getClientId`, `toString(byte[])`, `getMsb`, `getLsb`, and `toBytes(String)`.

## Control Flow
`getClientId()` generates a random UUID and writes MSB/LSB to a 16-byte `ByteBuffer`. `toString()` accepts null/empty as empty string, validates 16 bytes, reconstructs UUID pieces manually, and formats. `toBytes()` accepts null/empty as empty array or parses UUID string.

## State And Persistence
No mutable state. Client IDs are transmitted in RPC headers and can be represented as bytes or UUID strings.

## Dependencies And Integration Points
Used by `Client` for per-client identity and response validation. Depends on Java UUID/ByteBuffer and Guava preconditions.

## Risks
Null and empty encode to empty string/array rather than a 16-byte UUID, so callers must distinguish absent ID from generated ID. Manual MSB/LSB extraction must stay big-endian compatible with `ByteBuffer.putLong`.

## Test Signals
Tests should cover UUID bytes/string round trips, null/empty conversions, invalid lengths, invalid UUID strings, and compatibility with `UuidCodec`.
