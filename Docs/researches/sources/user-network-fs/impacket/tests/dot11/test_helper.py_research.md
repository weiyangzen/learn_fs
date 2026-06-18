# sources/user-network-fs/impacket/tests/dot11/test_helper.py

Purpose: Tests the descriptor/helper framework used to build `ProtocolPacket` classes.

Important APIs, types, and functions: Defines an inline `MockPacket` subclass of `impacket.helper.ProtocolPacket` using `Byte`, `Word`, `ThreeBytesBigEndian`, `Long`, and `Bit` descriptors plus `header_size` and `tail_size`.

Control flow: The test assigns descriptor-backed fields, checks readback, toggles a bit alias, and round-trips `get_packet()` through a new `MockPacket`.

State and persistence behavior: Descriptor state lives in the packet buffer in memory. No filesystem or network state.

Dependencies and integration points: Validates helper descriptors consumed by packet classes in `impacket.dot11` and related protocol modules.

Risks: Bit alias writes can overwrite adjacent byte-field content if masks are wrong. Round-trip serialization is the main guard against descriptor offset regressions.

Test signals: Small but useful signal for descriptor read/write behavior, bitfield aliasing, and packet reparse stability.
