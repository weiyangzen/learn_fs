# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Serializer.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 149 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Serializer`. Macros/constants: `MESSMER_CPPUTILS_DATA_SERIALIZER_H`. Important declarations or call sites include `Serializer(size_t size);`; `void writeBool(bool value);`; `void writeUint8(uint8_t value);`; `void writeInt8(int8_t value);`; `void writeUint16(uint16_t value);`; `void writeInt16(int16_t value);`; `void writeUint32(uint32_t value);`; `void writeInt32(int32_t value);`; `void writeUint64(uint64_t value);`; `void writeInt64(int64_t value);`. CMake commands used here include `Serializer`, `DISALLOW_COPY_AND_ASSIGN`, `writeUint8`, `if`, `writeUint64`, `_writeData`, `ASSERT`. Primary includes/dependencies visible in the file include `Data.h`, `FixedSizeData.h`, `../macros.h`, `../assert/assert.h`, `string`, `SerializationHelper.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`, `FixedSizeData.h`, `../macros.h`, `../assert/assert.h`, `string`, `SerializationHelper.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- Serializer preallocates the exact output size and refuses both overflow and underfilled output in `finished`.
