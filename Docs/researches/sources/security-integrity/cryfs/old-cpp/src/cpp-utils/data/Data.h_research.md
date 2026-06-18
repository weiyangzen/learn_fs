# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 205 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Allocator`, `DefaultAllocator`, `Data`. Macros/constants: `MESSMER_CPPUTILS_DATA_DATA_H_`. Important declarations or call sites include `virtual void* allocate(size_t size) = 0;`; `virtual void free(void* ptr, size_t size) = 0;`; `void* allocate(size_t size) override {`; `return std::malloc((size == 0) ? 1 : size);`; `void free(void* data, size_t /*size*/) override {`; `std::free(data);`; `explicit Data(size_t size, unique_ref<Allocator> allocator = make_unique_ref<DefaultAllocator>());`; `~Data();`; `Data copy() const;`; `Data copyAndRemovePrefix(size_t prefixSize) const;`. CMake commands used here include `Data`, `DISALLOW_COPY_AND_ASSIGN`, `if`, `_free`, `ASSERT`, `StoreToStream`. Primary includes/dependencies visible in the file include `cstdlib`, `boost/filesystem/path.hpp`, `boost/optional.hpp`, `../macros.h`, `memory`, `fstream`, `../assert/assert.h`, `../pointer/unique_ref.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cstdlib`, `boost/filesystem/path.hpp`, `boost/optional.hpp`, `../macros.h`, `memory`, `fstream`, `../assert/assert.h`, `../pointer/unique_ref.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- `Data` is move-only, allocator-backed, and exposes raw pointers; `dataOffset` is convenient but trusts callers to respect bounds.
