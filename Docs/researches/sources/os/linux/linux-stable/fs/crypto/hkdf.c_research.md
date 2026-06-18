# File Research: sources/os/linux/linux-stable/fs/crypto/hkdf.c

## Summary
Implements fscrypt's HKDF-SHA512 support. It initializes reusable HKDF extract state from fscrypt master keys or hardware-derived software secrets, then expands that state into domain-separated subkeys and identifiers.

## Main Responsibilities
- Compute HKDF-Extract using HMAC-SHA512 with a zero salt.
- Prepare a reusable `hmac_sha512_key` for repeated HKDF-Expand operations.
- Expand key material with `fscrypt\0` plus a fscrypt-specific context byte prepended to the caller's info string.
- Zero temporary pseudorandom key and partial-block buffers after use.

## Key APIs
- `fscrypt_init_hkdf()`: computes the HKDF pseudorandom key from master key material and prepares the HMAC key schedule.
- `fscrypt_hkdf_expand()`: implements RFC 5869 HKDF-Expand, including previous-block chaining, counter bytes, and fscrypt's context prefix.

## Important Behavior
Fscrypt performs HKDF-Extract even though master keys are expected to be pseudorandom. This permits shorter master keys for modes that do not need SHA-512-length input while keeping KDF behavior uniform across modes.

HKDF-Expand prepends `fscrypt\0` and a one-byte context to every info string. This prevents accidental reuse between derived outputs such as key identifiers, per-file contents keys, direct keys, IV_INO_LBLK keys, dirhash keys, and inode-number hash keys.

## Research Notes
The file is small but security-critical. Correctness depends on all callers choosing unique context/info combinations; `fscrypt_private.h` centralizes the context byte assignments used here.
