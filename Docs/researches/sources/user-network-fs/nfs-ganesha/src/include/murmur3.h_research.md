# sources/user-network-fs/nfs-ganesha/src/include/murmur3.h

## Purpose

`murmur3.h` declares the MurmurHash3 non-cryptographic hash routines used wherever the server needs stable, fast hashing of byte keys such as addresses, handles, or cache keys.

## Important APIs, Types, and Functions

The API consists of `MurmurHash3_x86_32`, `MurmurHash3_x86_128`, and `MurmurHash3_x64_128`. Each takes a key pointer, byte length, 32-bit seed, and caller-provided output buffer.

## Control Flow

Callers choose the width/architecture variant, provide an initialized output object of the expected size, and use the hash result for table indexing or key derivation. The header does not provide endian or size wrappers.

## State and Persistence Behavior

The hash functions are stateless. Persisting their output externally would create compatibility constraints around implementation version and seed choice.

## Dependencies and Integration Points

The only direct dependency is `<stdint.h>`. Implementations integrate with hash tables and cache subsystems. The public-domain notice means this file's licensing differs from most LGPL headers.

## Risks and Test Signals

Murmur3 is not suitable for authentication or adversarial collision resistance. Risks include output-buffer size mistakes, signed `int len` overflow for very large inputs, and platform/endian mismatches if persisted. Tests should compare known Murmur3 vectors for all variants, zero-length keys, unaligned buffers, different seeds, and architecture-specific output sizes.
