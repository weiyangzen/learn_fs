# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2_consts.h

## Role

Defines SHA-256 and SHA-512 round constants and architecture-dependent constant-loading macros.

## Key Interfaces

- Exports `sha256_consts[]` and `sha512_consts[]`.
- On SPARC, `SHA256_CONST(x)` and `SHA512_CONST(x)` load from arrays.
- On other architectures, they expand to immediate `SHA256_CONST_<x>` and `SHA512_CONST_<x>`.
- Defines all 64 SHA-256 constants and all 80 SHA-512 constants from FIPS 180-2.
- SHA-512 constants are also used for SHA-384.

## Risk Notes

These are algorithm constants. Any typo or mismatch changes digest output. The SPARC array path must remain synchronized with the macro constant set.
