# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/siphash.h

Declares the one-shot SipHash function.

Public API:
- `int siphash(const uint8_t *in, size_t inlen, const uint8_t *k, uint8_t *out, size_t outlen);`

Contract:
- `k` must point to a 16-byte key.
- `outlen` must be either 8 or 16 bytes; the implementation asserts this.
- Returns zero on success.
