# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataFixture.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 25 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `Data DataFixture::generate(size_t size, unsigned long long int seed) {`; `Data result(size);`; `for(size_t i=0; i<size/sizeof(unsigned long long int); ++i) {`; `serialize<unsigned long long int>(result.dataOffset(i*sizeof(unsigned long long int)), val);`; `uint64_t alreadyWritten = (size/sizeof(unsigned long long int))*sizeof(unsigned long long int);`; `serialize<unsigned char>(result.dataOffset(alreadyWritten + i), remainingBytes[i]);`. CMake commands used here include `for`. Primary includes/dependencies visible in the file include `DataFixture.h`, `SerializationHelper.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `DataFixture.h`, `SerializationHelper.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.
