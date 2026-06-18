# sources/storage-engines/foundationdb/flow/include/flow/Net2Packet.h

## Purpose
`Net2Packet.h` declares packet queue structures used by Flow's Net2 transport for unsent packet buffers and reliable-packet resend lists.

## Important APIs, Types, And Functions
Important types are `ReliablePacket`, `UnsentPacketQueue`, and `ReliablePacketList`. APIs include `ReliablePacket::insertBefore()`, `ReliablePacket::remove()`, `UnsentPacketQueue::getWriteBuffer()`, `setWriteBuffer()`, `prependWriteBuffer()`, `empty()`, `getUnsent()`, `sent()`, `discardAll()`, `ReliablePacketList::insert()`, `compact()`, and `discardAll()`.

## Control Flow
Writers append into the tail packet buffer from `getWriteBuffer()` and update the tail with `setWriteBuffer()`. Sending consumes bytes from `getUnsent()` through `sent()`. Reliable packets form a circular list and can be compacted into packet buffers for resend after connection close.

## State And Persistence Behavior
`ReliablePacket` stores buffer pointer, continuation chain, list links, and byte range. `UnsentPacketQueue` stores first/last unsent packet buffers and a queue-wait histogram. `ReliablePacketList` stores a sentinel node. Network data persists in packet buffers until sent, compacted, or discarded.

## Dependencies And Integration Points
It depends on `flow.h`, `Histogram`, `PacketBuffer`, and serialization packet writers declared elsewhere. It integrates with Net2 connection send queues and reliability/resend logic.

## Risks And Edge Cases
List and continuation ownership must be exact to avoid leaks or double deletes. `empty()` considers bytes-sent vs bytes-written on the first buffer, so partially sent buffers require careful `sent()` updates. Destructor poisons pointers for debug visibility.

## Test Signals
Tests should cover buffer append/prepend/send progression, discard cleanup, reliable insert/remove/compact, histogram sampling, partial send boundaries, and connection-close resend behavior.
