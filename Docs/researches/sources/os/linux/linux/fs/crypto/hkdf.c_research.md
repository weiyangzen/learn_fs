# File Research: sources/os/linux/linux/fs/crypto/hkdf.c

## Summary
Implements fscrypt’s HKDF-SHA512 support. It provides HKDF-Extract initialization for master keys or hardware-derived software secrets, and HKDF-Expand for deriving domain-separated fscrypt subkeys and identifiers.

## Main Responsibilities
- Initialize an `hmac_sha512_key` from master key material with HKDF-Extract.
- Expand the prepared HKDF key into output key material for specific fscrypt contexts.
- Prefix HKDF info strings with `fscrypt\0` and a context byte to prevent cross-purpose reuse.

## Key APIs
- `fscrypt_init_hkdf()`: computes PRK using HMAC-SHA512 with a zero salt, prepares reusable HMAC state, and zeroizes the temporary PRK.
- `fscrypt_hkdf_expand()`: implements RFC 5869 HKDF-Expand with SHA-512, supporting arbitrary output length up to the HKDF limit and wiping temporary partial-block output.

## Important Behavior
Fscrypt always performs HKDF-Extract even though master keys should already be pseudorandom. This permits shorter master keys for modes that do not require a full SHA-512-length input and keeps the KDF behavior uniform.

HKDF-Expand uses prior block chaining for multi-block output, appends a counter byte, and includes the fscrypt-specific prefix and context byte before caller-provided info. This design isolates derived outputs such as key identifiers, per-file keys, direct keys, dirhash keys, IV_INO_LBLK keys, and inode hash keys.

## Research Notes
This file is small but security-critical. The main correctness property is that every caller must use a unique context/info combination, and `fscrypt_private.h` centralizes those context IDs.
