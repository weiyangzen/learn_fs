# File Research: sources/os/bsd/freebsd-src/sys/sys/hash.h

## Purpose
Provides simple inline 32-bit string/buffer hashing helpers and kernel hash table allocation/hash algorithm declarations.

## Main Interfaces
- Default hash macros: `HASHINIT`, `HASHSTEP`.
- Inline hashes:
  - `hash32_buf`
  - `hash32_str`
  - `hash32_strn`
  - `hash32_stre`
  - `hash32_strne`
- Kernel `struct hashalloc_args` with version, error, size, bucket header size, hash type, head type, lock type, malloc flags/type, lock name, constructor, destructor.
- Kernel allocation APIs: `hashalloc`, `hashfree`.
- Kernel hash functions:
  - `jenkins_hash`
  - `jenkins_hash32`
  - `murmur3_32_hash`
  - `murmur3_32_hash32`

## Dependencies And Integration
Includes `sys/types.h`. The `*_stre` helpers are intended for pathname component hashing in `namei`-style code. Kernel allocation supports multiple bucket head types and lock strategies.

## Risk Notes
The inline `HASHSTEP` hash is simple and non-cryptographic. `hashalloc_args` versioning is present but currently version `0`; callers must inspect `error` after allocation attempts.
