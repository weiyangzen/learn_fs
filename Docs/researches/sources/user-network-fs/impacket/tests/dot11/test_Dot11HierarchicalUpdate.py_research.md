# sources/user-network-fs/impacket/tests/dot11/test_Dot11HierarchicalUpdate.py

## Purpose
This file tests `ProtocolPacket` parent/child composition semantics. It verifies that nested packet serialization, size calculations, body views, and parent-child references update correctly when a child or parent body is modified.

## Important APIs, Types, and Functions
`PacketTest` is a minimal `ProtocolPacket` subclass with fixed header size 7 and tail size 5. `TestDot11HierarchicalUpdate` uses `load_packet`, `contains`, `load_body`, `get_packet`, `get_size`, `get_header_size`, `get_body_size`, `get_tail_size`, `body.get_buffer_as_string`, `get_body_as_string`, `parent`, and `child`.

## Control Flow
`setUp()` builds three nested raw packets, loads them into `PacketTest` instances, and links `packet3 -> packet2 -> packet1` using `contains()`. Tests first verify initial serialization and sizes, then modify `packet1` body and check that ancestors reflect the new child bytes. The final test calls `packet2.load_body(...)` and verifies that replacing a parent body detaches the previous child.

## State and Persistence Behavior
State consists of in-memory packet buffers and hierarchy pointers. The important state transition is child detachment when a packet body is overwritten directly, preventing stale child references.

## Dependencies and Integration Points
The test depends on `impacket.dot11.ProtocolPacket`, but it exercises generic packet composition behavior used by dot11 and likely other packet layers.

## Risks
The synthetic packets use ASCII-size headers/tails and fixed sizes, so they validate hierarchy mechanics rather than protocol-specific parsing. Duplicate test method descriptions are benign but make failures less descriptive.

## Test Signals
Signals include exact serialized nested byte strings, exact size arithmetic before and after mutation, body-buffer propagation up the hierarchy, and correct parent/child pointer detachment.
