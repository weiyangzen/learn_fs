# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sha2.h

## Role

Declares SHA-2 context layout, digest/HMAC sizing constants, algorithm IDs, and SHA-256/384/512 function interfaces.

## Key Interfaces

- Digest lengths for SHA-256, SHA-384, SHA-512, SHA-512/224, and SHA-512/256.
- HMAC key and block-size constants.
- Algorithm constants from `SHA256` through `SHA512_256`.
- `SHA2_CTX` stores algorithm type, 32-bit or 64-bit state, 64-bit or 128-bit bit count, and 128-byte input buffer.
- Typedefs alias `SHA256_CTX`, `SHA384_CTX`, and `SHA512_CTX` to `SHA2_CTX`.
- Generic `SHA2Init()`, `SHA2Update()`, `SHA2Final()`.
- Algorithm-specific init/update/final functions for SHA-256, SHA-384, and SHA-512.
- Under `_SHA2_IMPL`, defines internal `sha2_mech_type_t`.

## Risk Notes

The internal mechanism enum order is used by division/modulus calculations in the module; adding or reordering mechanisms requires care. Consumers are told not to inspect context fields directly.
