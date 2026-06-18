## sources/test-tools/fio/crc/murmur3.c

Purpose: MurmurHash3 32-bit implementation for fio non-cryptographic hashing.

Important APIs and flow: `murmurhash3()` processes 4-byte blocks with constants `c1` and `c2`, rotates/mixes the running hash, then calls `murmur3_tail()` for 1-3 leftover bytes and final avalanche `fmix32()`. `fio_fallthrough` documents intentional switch fallthrough.

State and persistence: no state; seed is passed per call.

Dependencies and integration: includes `murmur3.h` and `compiler/compiler.h`. Used by fio hash/checksum testing or data-pattern selection.

Risks and test signals: block processing casts to `uint32_t *` and uses Murmur's negative-index loop pattern, which depends on architecture alignment tolerance and endian expectations. Known Murmur3 vectors and cross-platform tests are important.
