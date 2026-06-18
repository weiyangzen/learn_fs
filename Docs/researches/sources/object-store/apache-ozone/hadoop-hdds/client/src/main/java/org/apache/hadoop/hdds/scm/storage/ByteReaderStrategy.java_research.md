# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteReaderStrategy.java

## Purpose
`ByteReaderStrategy` is the minimal strategy interface used to unify byte-array and `ByteBuffer` read loops in Ozone stream classes.

## Important APIs and Types
It declares `readFromBlock(InputStream, int)` and `getTargetLength()`. Implementations include `ByteArrayReader` and `ByteBufferReader`.

## Control Flow
`ExtendedInputStream` wraps standard read methods into strategies, then calls subclass `readWithStrategy`. Block, multipart, and EC streams can repeatedly ask a strategy how much remains and delegate bounded reads to the current child stream.

## State and Persistence Behavior
The interface has no state. Implementations usually hold caller buffers and mutate remaining byte counts.

## Dependencies and Integration Points
It decouples stream traversal logic from target buffer type across `BlockInputStream`, `MultipartInputStream`, `ECBlockInputStream`, and wrappers.

## Risks
The contract relies on implementations updating `getTargetLength()` accurately after each read. EOF handling is not specified in the interface, so callers must enforce their own read/EOF invariants.

## Test Signals
Covered indirectly by all stream read tests using both byte arrays and NIO buffers.
