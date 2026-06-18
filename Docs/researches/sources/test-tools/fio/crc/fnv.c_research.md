## sources/test-tools/fio/crc/fnv.c

Purpose: implements fio's 64-bit FNV-style hash over unaligned data.

Important API and flow: `fnv(const void *buf, uint32_t len, uint64_t hval)` repeatedly multiplies the current hash by `FNV_PRIME`. It xors whole `uint64_t` chunks while enough bytes remain, then builds a big-endian-ish tail value from leftover bytes and xors it before returning.

State and persistence: no state; caller supplies seed/current `hval` for incremental behavior.

Dependencies and integration: depends on `fnv.h` and integer types. Used by fio hash/checksum selection and CRC/hash tests.

Risks and test signals: whole-word casts can be sensitive to alignment and host endianness expectations; the comment explicitly optimizes for not requiring 64-bit multiples, not for canonical FNV byte order. Known fio vectors and cross-architecture tests are useful.
