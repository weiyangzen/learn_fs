# sources/user-network-fs/libsmb2/lib/md4.h

## Purpose

`md4.h` declares the bundled RSA Data Security MD4 API used by libsmb2 for NTLM password hashing. NTLMv1/NTLMv2 derives the NT hash by applying MD4 to the UTF-16LE password, so this header is part of the authentication support surface rather than a general-purpose public crypto API.

## Important APIs, Types, And Functions

`MD4_CTX` stores four 32-bit chaining words, a 64-bit bit count split into two 32-bit words, and a 64-byte block buffer. The declared API is `MD4Init(MD4_CTX *)`, `MD4Update(MD4_CTX *, unsigned char *, unsigned int)`, and `MD4Final(unsigned char[16], MD4_CTX *)`.

## Control Flow

Callers initialize a context, feed one or more byte ranges, then finalize into a 16-byte digest. In this repository the direct consumer is `NTOWFv1` in `ntlmssp.c`, which converts a password to UTF-16 and hashes that buffer.

## State And Persistence Behavior

All state is caller-owned in `MD4_CTX`. The digest API has no file, network, heap, or global persistence. `MD4Final` in the implementation zeroizes the context after producing the digest.

## Dependencies And Integration Points

The header requires `uint32_t` to be available from configuration-driven includes in consumers; `md4c.c` includes `config.h`, `stdint.h`, `compat.h`, and this header. The integration point is NTLMSSP authentication, not SMB2 framing.

## Risks And Edge Cases

The update function accepts a mutable `unsigned char *` instead of `const unsigned char *`, which is an old API shape and can force casts in callers. MD4 is cryptographically broken and must be treated only as a protocol compatibility primitive for NTLM, never as a new integrity or password-storage primitive. Header consumers must ensure `stdint.h` or equivalent definitions are available before `MD4_CTX` is parsed.

## Test Signals

Test with RFC 1320 MD4 vectors, split updates versus one-shot updates, empty input, inputs around 55/56/63/64/65 bytes, and NTLM known password-to-NT-hash vectors through `ntlmssp.c`.
