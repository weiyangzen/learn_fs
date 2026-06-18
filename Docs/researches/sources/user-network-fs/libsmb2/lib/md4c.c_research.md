# sources/user-network-fs/libsmb2/lib/md4c.c

## Purpose

`md4c.c` is a bundled RFC 1320 MD4 implementation. It supplies the `MD4Init`, `MD4Update`, and `MD4Final` functions declared by `md4.h`, primarily so NTLMSSP can derive NT password hashes without depending on an external crypto library.

## Important APIs, Types, And Functions

The public functions are `MD4Init`, `MD4Update`, and `MD4Final`. Internal helpers include `MD4Transform` for the three MD4 compression rounds, `Encode` and `Decode` for little-endian 32-bit word conversion, and local loop-based `MD4_memcpy`/`MD4_memset`. Macros `F`, `G`, `H`, `ROTATE_LEFT`, `FF`, `GG`, and `HH` implement the MD4 round functions and rotations.

## Control Flow

`MD4Init` seeds the standard MD4 initial chaining state and clears the bit count. `MD4Update` updates the bit count, fills any partial 64-byte block, transforms full blocks, and stores remaining bytes in the context buffer. `MD4Final` encodes the original bit length, pads to 56 bytes modulo 64, appends the length, encodes the final state into a 16-byte digest, and zeroizes the context. `MD4Transform` decodes one 64-byte block into sixteen 32-bit words, runs all 48 MD4 operations over three rounds, adds the result back into the chaining state, and clears the temporary word array.

## State And Persistence Behavior

The only persistent state is the caller-provided `MD4_CTX` between calls. Static `PADDING` is read-only padding data. Finalization wipes the context and transform wipes the local decoded block. No heap allocations, file I/O, or network state are used.

## Dependencies And Integration Points

The file includes `config.h` when available, `stdint.h` when configured, `compat.h`, and `md4.h`. Its main integration is `NTOWFv1` in `ntlmssp.c`, which passes UTF-16 password bytes to `MD4Update`. It is built as part of the libsmb2 library.

## Risks And Edge Cases

MD4 is obsolete and collision-prone; the risk is acceptable only for NTLM protocol compatibility. The implementation assumes 32-bit arithmetic wraparound on `uint32_t`, which is standard for unsigned C integers. The API length type is `unsigned int`, so extremely large single updates depend on repeated calls and the split 64-bit count. The helper signatures are non-const for input buffers, reflecting the original implementation style.

## Test Signals

Use known MD4 vectors for empty string, `a`, `abc`, `message digest`, alphabet strings, and long numeric strings. Include incremental update tests that split input at every byte position around block boundaries. NTLM integration tests should verify the MD4 digest of UTF-16LE passwords matches known NT hashes.
