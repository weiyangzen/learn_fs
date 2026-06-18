<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/data.rs -->
# sources/object-store/garage/src/util/data.rs

## Purpose
Common byte-array, UUID, hash, and hashing utilities for Garage.

## Important APIs, types, and functions
`FixedBytes32` wraps `[u8; 32]` with custom serde bytes representation, debug hex formatting, slice access, `try_from`, `to_vec`, and lexicographic `increment`. Type aliases `Uuid` and `Hash` use it. Functions include `sha256sum`, `blake2sum`, `fasthash`, and `gen_uuid`.

## Control flow
Hash helpers feed data through SHA-256, Blake2s, or xxhash. `gen_uuid` fills random bytes. `increment` walks bytes from the end, carrying over and returning `None` on all-0xff overflow.

## State and persistence behavior
Fixed 32-byte values are serialized compactly and used as persistent identifiers/hashes in tables, network node IDs, and data placement logic.

## Dependencies and integration points
Integrates serde visitors, hex formatting, `garage_net::NodeID` conversions, `rand`, `sha2`, `blake2`, and `xxhash-rust`.

## Risks and test signals
`fasthash` is not cryptographic and should not be used where collision resistance matters. Tests cover increment edge cases; additional signals are serde round-trips and NodeID conversions.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/data.rs -->
