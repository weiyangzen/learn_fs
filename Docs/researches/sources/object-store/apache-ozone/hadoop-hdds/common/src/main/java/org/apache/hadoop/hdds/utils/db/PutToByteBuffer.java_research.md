# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/PutToByteBuffer.java

## Purpose
Package-private functional interface for writing source data into a `ByteBuffer` while reporting required size or unavailability.

## Important APIs, Types, And Functions
`PutToByteBuffer<E extends Exception>` extends Ratis `CheckedFunction<ByteBuffer, Integer, E>`.

## Control Flow
Implementations receive a `ByteBuffer`, may write full or partial data, return required size when source exists, and return null when the source is unavailable.

## State And Persistence
The interface owns no state. It is a callback over transient buffers.

## Dependencies And Integration Points
Used by `CodecBuffer.putFromSource`, `Buffer.getFromDb`, and `StringCodecBase` encoding.

## Risks
Implementations must report sizes consistently with bytes written. Returning negative sizes violates `CodecBuffer` preconditions. Partial writes require caller retry logic to be correct.

## Test Signals
Tests should exercise null result, exact result, required-size-larger-than-capacity, negative size rejection, and exception propagation.
