<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/city.h -->
# sources/user-network-fs/nfs-ganesha/src/include/city.h

## Purpose
`city.h` declares the C port of Google's CityHash non-cryptographic hash functions. It provides 64-bit and 128-bit hash APIs for byte arrays with optional seeds.

## Important APIs, types, and functions
- Local aliases `uint8`, `uint32`, and `uint64` map to fixed-width integer types.
- `struct _uint128`/`uint128` stores two 64-bit halves.
- `Uint128Low64()` and `Uint128High64()` macros access the two halves.
- `CityHash64()`, `CityHash64WithSeed()`, and `CityHash64WithSeeds()` compute 64-bit hashes.
- `CityHash128()` and `CityHash128WithSeed()` compute 128-bit hashes.

## Control flow
Callers pass a byte buffer and length, plus optional seed values. Implementations compute deterministic non-cryptographic hashes optimized for little-endian platforms and unaligned reads.

## State and persistence
The header has no state. Hash results may be persisted by callers as indexes or identifiers, but the header itself only declares pure functions.

## Dependencies and integration points
It depends on `<stdlib.h>` and `<stdint.h>`. It can be used by hash tables, fingerprinting, or cache/index code that needs fast non-cryptographic hashing.

## Risks
- Comments explicitly state CityHash is not suitable for cryptography.
- The vendored code warns it has not been tested on big-endian platforms.
- Persisted hash values may change if the implementation is updated or if platform-specific behavior differs.
- Local type aliases can collide with other headers in broad include contexts.

## Test signals
- Known-vector tests should verify 64-bit and 128-bit results for representative inputs and seeds.
- Portability tests should run on architectures with strict alignment and different endianness if supported.
- Security reviews should ensure CityHash is not used for authentication, signatures, or attacker-controlled hash-flood-sensitive tables without mitigation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/city.h -->
