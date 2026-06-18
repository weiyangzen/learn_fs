# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/SerializationHelperTest.cpp

Purpose: Tests typed serialization/deserialization helpers for integers, floats, doubles, structs, one-byte structs, alignment, unaligned offsets, negative values, and explicit offsets.

Important APIs and types: Uses `SerializationHelper`, `Data`, GoogleTest, and local structs `DataStructure` and `OneByteStruct`.

Control flow: Each test writes a value into a `Data` buffer at aligned or unaligned positions, reads it back, and checks equality. Signed/unsigned integer widths from 8 to 64 bits and floating-point types are covered.

State and persistence behavior: State is in-memory binary buffers. No endian conversion persistence files are produced.

Dependencies and integration points: Serialization helpers are used anywhere CryFS stores typed values inside raw `Data` buffers.

Risks: Tests generally validate roundtrip on the host platform, so cross-endian or ABI packing expectations need separate known-byte tests if required. Struct serialization depends on layout.

Test signals: Correct roundtrip for every primitive width, aligned/unaligned offset handling, struct roundtrip, and offset-specific deserialize behavior.
