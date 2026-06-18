# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 73 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `optional<Data> Data::LoadFromFile(const bf::path &filepath) {`; `ifstream file(filepath.string().c_str(), ios::binary);`; `if (!file.good()) {`; `optional<Data> result(LoadFromStream(file));`; `if (!file.good()) {`; `throw std::runtime_error("Error reading from file");`; `std::streampos Data::_getStreamSize(istream &stream) {`; `auto current_pos = stream.tellg();`; `stream.seekg(0, stream.end);`; `auto endpos = stream.tellg();`. CMake commands used here include `if`, `ASSERT`. Primary includes/dependencies visible in the file include `Data.h`, `stdexcept`, `vendor_cryptopp/hex.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`, `stdexcept`, `vendor_cryptopp/hex.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.
