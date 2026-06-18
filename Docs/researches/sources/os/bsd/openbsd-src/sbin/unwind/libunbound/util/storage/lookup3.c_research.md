# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/lookup3.c

Contains Bob Jenkins’ public-domain lookup3 hash, adapted for Unbound.

Active public behavior:
- `hash_set_raninit(v)` sets a process-global randomized initial value used by later hashes.
- `hashword(k, length, initval)` hashes arrays of `uint32_t`.
- `hashlittle(key, length, initval)` hashes arbitrary byte arrays to a 32-bit value.
- Hash state initialization incorporates `raninit`, input length, and caller-provided `initval`.

Implementation details:
- Endianness is determined via configured target endianness when available, otherwise via platform macros and system headers.
- `mix` and `final` macros perform Jenkins’ reversible mixing/final avalanche operations.
- `ARRAY_CLEAN_ACCESS` is always enabled here, so tail reads avoid intentional overread/mask tricks; this favors auditability and valgrind cleanliness.
- `hashlittle` has optimized paths for little-endian 32-bit aligned input, little-endian 16-bit aligned input, and byte-by-byte fallback.
- `hashbig` is present inside `#if 0` and is not compiled.
- `hashword2`, `hashlittle2`, and test drivers are compiled only under `SELF_TEST`.

Security and usage notes:
- The comments explicitly say lookup3 is not cryptographic.
- The randomized `raninit` is Unbound-specific hardening against predictable hash placement.
- The global seed should be set before threads and before hashing persistent structures, because changing it changes all subsequent hash results.
