# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/MockGatheringChannel.java

## Purpose
Implements a test `GatheringByteChannel`/`WritableByteChannel` that captures writes and can simulate partial write behavior.

## Important APIs, types, and functions
- Implements `write(ByteBuffer)`, `write(ByteBuffer[])`, `write(ByteBuffer[], int, int)`, `isOpen`, and `close`.
- Uses `adjustedWrite` to limit or randomize the number of bytes accepted.
- Exposes behavior for tests that need gathering-channel semantics without real IO.

## Control flow
Write methods iterate through buffers, compute allowed write size, copy bytes from source buffers into an internal sink or counters, and return the number of bytes written. `close` flips channel state; `isOpen` reports it.

## State and persistence behavior
State is in-memory channel-open status and captured/counted bytes. No disk or socket IO occurs.

## Dependencies and integration points
Used by chunk buffer and codec tests to verify write-to-channel behavior and partial-write handling.

## Risks and test signals
If the mock diverges from `GatheringByteChannel` semantics, tests may pass unrealistic write loops. Partial-write simulation is the key integration signal.
