<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/WipedString.cpp -->
# sources/storage-engines/foundationdb/flow/WipedString.cpp
- Purpose: Unit tests for secure wiping of `WipedString` contents and serialized packet buffers containing wiped fields.
- Important APIs/types/functions: Tests `/flow/WipedString/basic`, `/flow/WipedString/serialize/modest`, `/flow/WipedString/serialize/maximal`, helper `fillRandom` overloads, structs `WS_A`, `WS_B`, `WS_C`, and `testWipeAfterPacketSerialize`.
- Control flow: The basic test constructs random `WipedString`s under a keepalive allocator scope and asserts destroyed contents are zero. Serialization tests generate objects with embedded, optional, and vector `WipedString` fields, serialize through `PacketWriter`, inspect registered wiped areas before discard, discard packet buffers, and assert the sensitive regions were zeroed.
- State and persistence behavior: Uses keepalive allocator state to keep freed memory inspectable and its wiped-area set as the verification surface. No persistent output.
- Dependencies and integration points: Depends on `WipedString`, object serializer, packet writer/queue, `keepalive_allocator`, Flow network protocol version, deterministic randomness, and unit-test infrastructure.
- Risks: Tests rely on allocator behavior that intentionally keeps memory alive; they are not representative of normal allocation lifetimes. The random double helper reinterprets random bits, which may produce unusual floating values but only serialization is under test.
- Test signals: Embedded tests directly validate destructor wiping and serialization-context wiping for modest and large object graphs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/WipedString.cpp -->
