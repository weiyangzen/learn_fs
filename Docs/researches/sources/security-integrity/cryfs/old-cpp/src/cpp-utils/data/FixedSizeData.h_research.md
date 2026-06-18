# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/FixedSizeData.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 159 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `FixedSizeData`. Macros/constants: `MESSMER_CPPUTILS_DATA_FIXEDSIZEDATA_H_`. Important declarations or call sites include `static FixedSizeData<SIZE> Null();`; `static FixedSizeData<SIZE> FromString(const std::string &data);`; `std::string ToString() const;`; `static FixedSizeData<SIZE> FromBinary(const void *source);`; `void ToBinary(void *target) const;`; `const unsigned char *data() const;`; `unsigned char *data();`; `FixedSizeData<size> take() const;`; `FixedSizeData<SIZE - size> drop() const;`; `FixedSizeData() : _data() {}`. CMake commands used here include `FixedSizeData`, `ASSERT`, `static_assert`. Primary includes/dependencies visible in the file include `vendor_cryptopp/hex.h`, `string`, `array`, `cstring`, `../assert/assert.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `vendor_cryptopp/hex.h`, `string`, `array`, `cstring`, `../assert/assert.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.
