# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/PartInputStream.java

## Purpose
`PartInputStream` defines the minimal contract for a stream that can be a part of `MultipartInputStream`.

## Important APIs and Types
It extends Hadoop `CanUnbuffer` and `Seekable`, declares `getLength()` and `close()`, and provides a default `getRemaining()` as `getLength() - getPos()`.

## Control Flow
`MultipartInputStream` treats each part as a seekable segment, using `getRemaining()` to decide when to advance to the next part and `seek` to position within a selected segment.

## State and Persistence Behavior
The interface has no state. Implementations maintain their own positions, buffers, and clients.

## Dependencies and Integration Points
Implemented by block-level input streams such as `BlockExtendedInputStream` descendants. It is the direct composition boundary for multipart reads.

## Risks
`getRemaining()` assumes `getPos()` never exceeds length. Implementations must keep position and length coherent after failed reads, unbuffer, and close.

## Test Signals
Covered through `MultipartInputStream`, block input, stream block input, and EC block input tests.
