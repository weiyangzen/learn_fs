# sources/user-network-fs/nfs-ganesha/src/support/murmur3.c

## Purpose
This file embeds Austin Appleby's public-domain MurmurHash3 implementations used by NFS-Ganesha support code where fast non-cryptographic hashing is needed. It provides the x86 32-bit, x86 128-bit, and x64 128-bit variants and is intentionally platform-light except for endian/alignment assumptions hidden behind `getblock`.

## Important APIs, Types, And Functions
The exported functions are `MurmurHash3_x86_32`, `MurmurHash3_x86_128`, and `MurmurHash3_x64_128`, declared through `murmur3.h`. Internal helpers `rotl32`, `rotl64`, `fmix32`, and `fmix64` implement bit rotations and final avalanche mixing. Macros `ROTL32`, `ROTL64`, `BIG_CONSTANT`, and `getblock` keep the reference algorithm readable. Inputs are raw byte buffers, an `int len`, a `uint32_t seed`, and an output buffer supplied by the caller.

## Control Flow
Each hash routine splits input into fixed-size blocks, mixes full blocks with variant-specific constants, folds remaining tail bytes through fall-through `switch` cases, xors in the total length, applies final avalanche mixing, and writes the result to `out`. The x86 128-bit variant uses four 32-bit lanes, while the x64 variant uses two 64-bit lanes and walks blocks forward.

## State And Persistence
The implementation is stateless and has no persistence. All state is stack-local hash lanes and constants. The only observable side effect is writing the hash value into the caller-provided output buffer.

## Dependencies And Integration Points
It depends on `config.h` and `murmur3.h` for build configuration and prototypes. Callers must provide suitably sized output storage: 4 bytes for x86_32 and 16 bytes for the 128-bit variants. Hash consumers elsewhere in the tree rely on stable algorithm outputs, so changing constants, endian handling, or tail logic would break persisted hash keys if any external store uses the values.

## Risks And Test Signals
Risks are typical for the reference MurmurHash3 C implementation: unaligned reads through `uint32_t *` and `uint64_t *`, little-endian assumptions in `getblock`, signed `int len`, direct casts for output stores, and deliberate fall-through switches that can be broken by warning-driven edits. Test signals should include known MurmurHash3 vectors for empty strings, short tails of every length modulo 16, long multi-block inputs, different seeds, and builds on strict-alignment or big-endian targets if those are supported.
