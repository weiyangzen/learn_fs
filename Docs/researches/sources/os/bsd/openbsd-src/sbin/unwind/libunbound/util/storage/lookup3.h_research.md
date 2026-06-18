# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.h

Declares the lookup3 hashing API.

Public API:
- `hashword(const uint32_t *k, size_t length, uint32_t initval)`.
- `hashlittle(const void *k, size_t length, uint32_t initval)`.
- `hash_set_raninit(uint32_t v)`.

Contract:
- `hashword` length is measured in 32-bit words.
- `hashlittle` length is measured in bytes.
- `initval` supports chained or caller-seeded hashing.
- `hash_set_raninit` must be called before threaded use and before hashing stored data whose lookup depends on stable hash values.
