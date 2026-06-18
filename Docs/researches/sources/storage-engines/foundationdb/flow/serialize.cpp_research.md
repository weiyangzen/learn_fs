# sources/storage-engines/foundationdb/flow/serialize.cpp

## Purpose
`serialize.cpp` implements small runtime checks and Flow unit tests for serialization compatibility. It validates protocol-version assumptions, bounds-checks binary reads, and tests that data written by newer object serialization remains readable by older struct definitions during downgrade scenarios.

## Important APIs, Types, And Functions
Runtime functions are `_AssumeVersion::_AssumeVersion(ProtocolVersion version)` and `BinaryReader::readBytes(int bytes)`. Test-only types `_Struct`, `OldStruct`, and `NewStruct` define a shared `file_identifier`, old and new serialized fields, `setFields`, `isSet`, and `serialize` methods. `verifyData` reads serialized vectors through both `BinaryReader` and `ArenaReader`. Unit tests are `flow/serialize/Downgrade/WriteOld` and `flow/serialize/Downgrade/WriteNew`.

## Control Flow
`_AssumeVersion` rejects invalid protocol versions by asserting non-simulation, logging `SerializationFailed` with the invalid version and backtrace, then throwing `serialization_failed`. `BinaryReader::readBytes` computes the requested end pointer, logs and throws if it would pass `end`, otherwise advances `begin` and returns the previous pointer. Downgrade tests serialize a random number of old or new objects, then read them as `OldStruct` and verify only the old field semantics.

## State And Persistence
Serialization state lives in reader/writer instances, arenas, and buffers. `_AssumeVersion` stores the validated protocol version in `v`. `BinaryReader` mutates its `begin` cursor. The tests use transient vectors and serialized buffers only; there is no persistent storage.

## Dependencies And Integration Points
The file depends on `flow/network.h` for `g_network` and protocol version, `flow/serialize.h` for reader/writer/archive APIs, and `flow/UnitTest.h` for Flow tests. It integrates with Flow's object serializer flag on `ProtocolVersion`, `ObjectWriter`, `BinaryWriter`, `ArenaReader`, `serializer`, and FoundationDB's error/trace system.

## Risks
Error reporting intentionally lacks detailed expected-versus-actual serialization context, as noted by the file comments. `BinaryReader::readBytes` trusts `bytes` to be nonnegative; negative values would move the cursor backward if reachable. The failure paths assert non-simulation before throwing, so behavior differs under simulation. Downgrade compatibility depends on field ordering and archive behavior preserving known fields while ignoring new ones.

## Test Signals
The embedded downgrade tests verify old-writer/old-reader and new-object-writer/old-reader compatibility across both `BinaryReader` and `ArenaReader`. Additional useful signals include malformed/truncated buffer tests, invalid protocol-version tests outside simulation, negative-size defensive tests if the API can receive untrusted sizes, and cross-version serialized fixture tests.
