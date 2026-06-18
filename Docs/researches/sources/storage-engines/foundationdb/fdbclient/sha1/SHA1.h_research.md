# sources/storage-engines/foundationdb/fdbclient/sha1/SHA1.h

## Purpose
This header declares the `SHA1` C++ class and its internal constants/state. It is the public interface for the SHA-1 implementation in `SHA1.cpp`.

## Important APIs, Types, And Functions
The public API exposes construction, `update` from `std::string`, `update` from `std::istream`, `final`, and static `from_string`. Internal aliases `uint32` and `uint64` use fixed-width integer types. Constants define five digest words, sixteen 32-bit block words, and sixty-four bytes per block.

## Control Flow
Callers construct an instance, call one or more `update` methods, then call `final()` to retrieve and reset the digest. The private helpers declare the compression and buffer-conversion steps used by the implementation.

## State And Persistence Behavior
`digest`, `buffer`, and `transforms` hold mutable in-memory hashing state. There is no file, network, or database persistence.

## Dependencies And Integration Points
The header depends on `<iostream>`, `<string>`, and `<stdint.h>`. It is designed as a standalone utility class and returns `std::string` for easy integration with FoundationDB code that already uses string-like binary buffers.

## Risks And Edge Cases
The binary return value from `final()` is easy to misinterpret as text. The class is mutable and not thread-safe. SHA-1 should only be used for compatibility or non-adversarial checks.

## Test Signals
Compilation users should include this header without additional crypto dependencies. Behavioral tests should exercise incremental updates, stream updates, empty input, and multiple `final()` calls on one instance.
