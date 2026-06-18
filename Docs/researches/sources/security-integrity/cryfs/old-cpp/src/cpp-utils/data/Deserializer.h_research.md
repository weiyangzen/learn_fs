# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Deserializer.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 151 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Deserializer`. Macros/constants: `MESSMER_CPPUTILS_DATA_DESERIALIZER_H`. Important declarations or call sites include `Deserializer(const Data *source);`; `bool readBool();`; `uint8_t readUint8();`; `int8_t readInt8();`; `uint16_t readUint16();`; `int16_t readInt16();`; `uint32_t readUint32();`; `int32_t readInt32();`; `uint64_t readUint64();`; `int64_t readInt64();`. CMake commands used here include `Deserializer`, `DISALLOW_COPY_AND_ASSIGN`, `if`, `static_assert`, `_readData`. Primary includes/dependencies visible in the file include `Data.h`, `../macros.h`, `../assert/assert.h`, `FixedSizeData.h`, `SerializationHelper.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`, `../macros.h`, `../assert/assert.h`, `FixedSizeData.h`, `SerializationHelper.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- Deserializer cursor advancement is strict: primitive and data reads throw on overflow and `finished` throws when trailing bytes remain.
