# sources/user-network-fs/libsmb2/lib/md5.c

## Purpose

`md5.c` is a bundled Colin Plumb public-domain MD5 implementation. In this source set it supports NTLMSSP-related HMAC-MD5 operations indirectly through the library's MD5/HMAC code, not SMB2 packet framing by itself.

## Important APIs, Types, And Functions

The public API is `MD5Init`, `MD5Update`, `MD5Final`, and `MD5Transform`. On big-endian builds, `byteSwap` converts words between host order and MD5 little-endian order; on little-endian builds it is a no-op macro. Internal macros `F1` through `F4` and `MD5STEP` implement the four MD5 rounds.

## Control Flow

`MD5Init` seeds the four standard MD5 chaining words and clears the byte counter. `MD5Update` accumulates bytes into `ctx->in`, transforms a completed first partial block, processes all full 64-byte blocks, and stores the tail. `MD5Final` appends `0x80`, zero padding, and the 64-bit bit count, transforms the final block, byte-swaps the digest words if needed, copies 16 digest bytes to the caller, and clears the context. `MD5Transform` performs the full 64-step compression function over one 512-bit block.

## State And Persistence Behavior

All mutable state lives in the caller-provided `struct MD5Context`: four digest words, a two-word byte count, and a sixteen-word input block. `MD5Final` clears the context after digest extraction. There is no heap allocation, global mutable state, file I/O, or network behavior.

## Dependencies And Integration Points

The file includes optional `config.h`, `sys/types.h`, `compat.h`, and `md5.h`. `md5.h` supplies `UWORD32`, `md5byte`, endianness configuration, and the context layout. NTLMSSP uses HMAC-MD5 via `hmac-md5.c`, which depends on this MD5 implementation.

## Risks And Edge Cases

MD5 is cryptographically broken for collision resistance and should only be used where the protocol requires it, such as NTLMv2 HMAC-MD5 compatibility. The byte counter is two 32-bit words and update length is `unsigned`, so very large streams rely on correct carry behavior across repeated calls. Endianness behavior depends on `__BYTE_ORDER` and platform defines from configuration; big-endian and unusual console targets need explicit build/test coverage. Context clearing in `MD5Final` helps but does not wipe caller copies of input or digest.

## Test Signals

Use RFC 1321 MD5 vectors, split update tests around 56- and 64-byte boundaries, long multi-block inputs, and big-endian byte-swap tests where possible. Integration tests should verify HMAC-MD5 outputs used by NTLMv2 response generation and verification.
