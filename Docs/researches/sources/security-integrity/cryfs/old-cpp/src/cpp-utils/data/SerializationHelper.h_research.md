# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/SerializationHelper.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 79 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `DataType`, `Enable`, `serialize`, `deserialize`. Macros/constants: `MESSMER_CPPUTILS_DATA_SERIALIZATIONHELPER_H`. Important declarations or call sites include `constexpr bool greater_than(size_t lhs, size_t rhs) {`; `static_assert(std::is_pod<DataType>::value, "Can only serialize PODs");`; `static void call(void *dst, const DataType &obj) {`; `static_assert(std::is_pod<DataType>::value, "Can only serialize PODs");`; `static void call(void *dst, const DataType &obj) {`; `std::memcpy(dst, &obj, sizeof(DataType));`; `static_assert(std::is_pod<DataType>::value, "Can only serialize PODs");`; `static DataType call(const void *src) {`; `static_assert(std::is_pod<DataType>::value, "Can only deserialize PODs");`; `static DataType call(const void *src) {`. CMake commands used here include `static_assert`. Primary includes/dependencies visible in the file include `type_traits`, `cstring`, `cstdint`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `type_traits`, `cstring`, `cstdint`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.
