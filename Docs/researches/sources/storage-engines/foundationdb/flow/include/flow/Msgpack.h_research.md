# sources/storage-engines/foundationdb/flow/include/flow/Msgpack.h

## Purpose
`Msgpack.h` implements small MessagePack serialization helpers for Flow request/metric payloads.

## Important APIs, Types, And Functions
Important items are `MsgpackBuffer`, `serialize_bool()`, `serialize_value()`, `serialize_string()`, `serialize_vector()`, `serialize_map()`, and `serialize_ext()`.

## Control Flow
`MsgpackBuffer` grows by doubling when writes exceed capacity. Scalar serialization writes a type byte followed by big-endian bytes. String/vector/map helpers choose MessagePack fix/8/16/32 prefixes based on length. `serialize_ext()` reserves four length bytes, serializes payload through a callback, then patches the length.

## State And Persistence Behavior
The buffer owns a byte array, current data size, and capacity. Serialized bytes persist in memory until reset or buffer destruction. `reset()` clears only the size, not allocated capacity.

## Dependencies And Integration Points
It depends on `Trace`, `Error`, `network.h`, memory utilities, and STL algorithms. It integrates with REST/metrics or protocol code that emits MessagePack without a full external encoder.

## Risks And Edge Cases
`MsgpackBuffer::buffer_size` must be initialized nonzero before writes or resize loops cannot grow. Very large strings/maps warn and assert-we-think rather than fully supporting all MessagePack sizes. Direct endian byte extraction assumes host integer layout but writes explicit big-endian order.

## Test Signals
Golden MessagePack byte tests for bools, integers, strings at boundary sizes, vectors, maps, ext payload length patching, resize behavior, oversized warnings, and decoder round trips are useful.
