# sources/storage-engines/pebble/sstable/colblk/uints_encode.go

## Purpose
Defines a generic unsafe integer encoder used to write native integer slices directly into target buffers and finalize them into little-endian byte order.

## Important APIs, Types, and Functions
- `serializedUint` constrains the storable integer widths to uint8/16/32/64.
- `uintsEncoder[T]` wraps a typed view over a byte buffer.
- `makeUintsEncoder` checks alignment and capacity and returns a typed slice view.
- `UnsafeSet`, `CopyFrom`, `Len`, and `Finish` populate and finalize the encoded data.

## Control Flow
The constructor builds an unsafe typed slice over `targetBuf`. Callers set values with `UnsafeSet` or `CopyFrom`; `Finish` is a no-op on little-endian platforms and reverses byte order for 2-, 4-, or 8-byte elements on big-endian platforms.

## State and Persistence Behavior
The encoder writes directly into the final serialized buffer. It has no ownership of the buffer and no separate persistence layer. The final bytes are expected to be little-endian regardless of host architecture.

## Dependencies and Integration Points
Supports uint-column and other fixed-width column encoders. Depends on shared `BigEndian`, byte-reversal helpers, alignment constants, and invariant-only bounds checks.

## Risks and Edge Cases
Bad alignment or undersized buffers panic. `UnsafeSet` omits normal bounds checks outside invariant builds. Callers must always invoke `Finish` before treating the buffer as serialized data on big-endian machines.

## Test Signals
Covered indirectly by uint column tests and unsafe uint tests, including encoded data validation through decoders.
