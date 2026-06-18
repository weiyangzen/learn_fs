# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/UUIDv7.java

## Purpose

`UUIDv7` generates time-ordered UUID version 7 values using the current millisecond timestamp and random trailing bytes.

## APIs and control flow

`randomBytes()` fills 16 bytes with secure random data, writes the low 48 bits of `System.currentTimeMillis()` into bytes 0 through 5, then sets version 7 and RFC variant bits. `randomUUID()` wraps the byte array in a `ByteBuffer`, reads two longs, and constructs a Java `UUID`.

## State, dependencies, and integration

State is a thread-local `SecureRandom`. Dependencies are Java `ByteBuffer`, `SecureRandom`, and `UUID`. It integrates with ID-generation paths that benefit from roughly sortable UUIDs.

## Risks and test signals

UUIDv7 monotonicity within the same millisecond is not guaranteed because the random tail is not incremented. Clock rollback can break ordering. Tests should validate version/variant bits, timestamp placement, UUID-byte round trip, and ordering only across distinct milliseconds.
