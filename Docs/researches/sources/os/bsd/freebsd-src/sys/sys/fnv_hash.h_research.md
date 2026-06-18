# File Research: sources/os/bsd/freebsd-src/sys/sys/fnv_hash.h

## Purpose
Provides inline Fowler/Noll/Vo hash implementations for 32-bit and 64-bit buffers and strings.

## Main Interfaces
- Types: `Fnv32_t`, `Fnv64_t`.
- Constants: `FNV1_32_INIT`, `FNV1_64_INIT`, `FNV_32_PRIME`, `FNV_64_PRIME`.
- Functions:
  - `fnv_32_buf`
  - `fnv_32_str`
  - `fnv_64_buf`
  - `fnv_64_str`

## Dependencies And Integration
Assumes `u_int*` types and `size_t` are available from including context. Used where a compact non-cryptographic hash is sufficient.

## Risk Notes
This is not a security hash. The implementation multiplies then XORs each byte, matching FNV-1 rather than FNV-1a.
