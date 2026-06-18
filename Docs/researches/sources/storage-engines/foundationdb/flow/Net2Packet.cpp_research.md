# sources/storage-engines/foundationdb/flow/Net2Packet.cpp research

## Purpose

`Net2Packet.cpp` implements packet-buffer bookkeeping for Flow's network serialization path. It is concerned with writing serialized bytes across chained `PacketBuffer` objects, reserving split write space, tracking unsent buffers, and maintaining a list of reliable packets that can be compacted or discarded. The code is low-level infrastructure used by packet-oriented network layers rather than user-facing protocol logic.

## Important APIs, types, and functions

`PacketWriter::init` attaches a writer to a `PacketBuffer` and optional `ReliablePacket`, initializes length accounting relative to current `bytes_written`, and addrefs the buffer for reliable resend tracking. `PacketWriter::finish` finalizes length and reliable-packet end offsets. `serializeBytesAcrossBoundary` copies a byte range over as many buffers as needed. `nextBuffer` allocates a new `PacketBuffer` and extends the reliable `cont` chain when reliability is enabled. `writeAhead` reserves exactly a requested number of bytes, possibly split between current and next buffer, and returns a `SplitBuffer` describing the writable spans.

`SplitBuffer::write`, `write(data, len, offset)`, and `writeAndShrink` copy bytes into one or two reserved spans. `ReliablePacket::insertBefore` and `remove` manage the circular reliable-packet list and delete a packet plus its continuation chain while dropping buffer references. `UnsentPacketQueue::sent` advances `bytes_sent`, removes fully sent buffers, samples queue latency, and delrefs completed buffers. `UnsentPacketQueue::discardAll` drops all unsent buffers. `ReliablePacketList::compact` copies already-sent reliable ranges into a new packet-buffer chain and rewrites reliable packet metadata to point at compacted buffers. `ReliablePacketList::discardAll` repeatedly removes reliable packets from the sentinel list.

## Control flow

The normal write path starts with `UnsentPacketQueue::getWriteBuffer`, then `PacketWriter::init`, serialization calls, and `PacketWriter::finish`. If serialization exceeds the current buffer, `nextBuffer` appends a new buffer and, when reliable tracking is active, creates a continuation `ReliablePacket` for the new buffer segment. Later, socket write completion calls `UnsentPacketQueue::sent(bytes)`, which consumes bytes from the front buffer and releases whole buffers as they become fully sent. For reliable data, connection close/retry code can use `ReliablePacketList::compact(into, stopAt)` to copy sent reliable bytes into a compact chain while stopping before the still-unsent range.

## State and persistence behavior

All state is in memory and reference-counted through `PacketBuffer::addref`/`delref`. `PacketWriter` temporarily owns current buffer, reliable pointer, and length accounting. `UnsentPacketQueue` owns a linked range of packet buffers from `unsent_first` to `unsent_last`; the last buffer may still have writable capacity. Reliable state is a circular linked list with a sentinel `ReliablePacket`, and each reliable packet may have a `cont` chain for bytes split across buffers. There is no durable persistence, but incorrect reference counting here can leak or prematurely free packet memory.

## Dependencies and integration points

The file depends on `flow/Net2Packet.h`, `PacketBuffer` from the serialization infrastructure, `Histogram` for queue latency, and Flow allocation/assertion helpers. It integrates with network connection send queues and resend/reconnect behavior. `SendBuffer`/packet serialization code writes into these buffers; socket completion code reports sent byte counts back into `UnsentPacketQueue`.

## Risks and edge cases

The code assumes byte counts are exact and positive where required. `writeAhead` handles only one boundary crossing because it allocates a next buffer sized for the remaining bytes; callers must respect the returned `SplitBuffer` size. `SplitBuffer` performs raw `memcpy` without bounds checks beyond caller-provided lengths. Reliable compaction mutates packet metadata while iterating and splits packets if the destination buffer has insufficient unwritten space; bugs there would corrupt resend data or leak references. `UnsentPacketQueue::sent` treats a fully written buffer that still has unwritten capacity and no next buffer specially, preserving the tail write buffer instead of dropping it.

## Test signals

There are no inline unit tests in this file. Useful tests should exercise serialization that exactly fills a buffer, crosses one boundary, crosses multiple boundaries through `serializeBytesAcrossBoundary`, uses `writeAhead` plus `SplitBuffer::writeAndShrink`, partially and fully drains `UnsentPacketQueue::sent`, and compacts reliable packets with and without packet splits. Histogram sampling on sent buffers is an observable metric signal for queue latency.
