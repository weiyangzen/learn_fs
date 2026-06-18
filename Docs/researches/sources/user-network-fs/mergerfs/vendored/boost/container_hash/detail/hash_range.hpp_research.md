# sources/user-network-fs/mergerfs/vendored/boost/container_hash/detail/hash_range.hpp

Purpose: Implements the internal `boost::hash_detail::hash_range(seed, first, last)` engine used by public `boost::hash_range` and range-based `hash_value` overloads. It provides a generic element-by-element path and optimized byte-range paths.

Important APIs, types, and functions: `is_char_type`, `read32le`, `read64le`, `mul32`, and overloaded `hash_range` templates selected by iterator value type, iterator category, and `std::size_t` width. Character-like inputs include `char`, signed/unsigned char, C++20 `char8_t`, and `std::byte` when available.

Control flow: Non-byte ranges loop over elements and call `hash_combine`. Byte ranges use fixed little-endian block readers, mix 4-byte chunks on 32-bit platforms or 8-byte chunks on 64-bit platforms, handle tail bytes without out-of-bounds reads, then finalize with multiplication/xor mixing.

State and persistence behavior: Stateless and header-only; the only carried state is the caller-provided seed and local mixing accumulators.

Dependencies and integration points: Depends on `hash_fwd.hpp`, `mulx.hpp`, iterator traits, integer limits, and C string memory helpers. Integrated by `hash.hpp` for strings, vectors, arrays, and generic containers.

Risks: Hash output is ABI/behavioral surface for unordered containers and persisted hash tests. Tail-byte and endian logic are sensitive, and optimized byte paths require valid iterator category/value-type detection.

Test signals: Compile under 32-bit and 64-bit targets; compare known hashes for empty, short, aligned, and unaligned byte ranges; verify non-random-access byte iterators; check that generic element ranges still call `hash_combine`.
