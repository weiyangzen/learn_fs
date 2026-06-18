# File Research: sources/os/linux/linux-stable/fs/crypto/keysetup_v1.c

## Summary
Implements compatibility key setup for original fscrypt v1 policies. It supports the legacy AES-128-ECB nonce-based per-file KDF, process-subscribed logon key lookup, and v1 DIRECT_KEY caching through a global direct-key table.

## Main Responsibilities
- Search current task subscribed keyrings for v1 `logon` keys with fscrypt or filesystem legacy prefixes.
- Validate legacy `struct fscrypt_key` payload size and minimum key length.
- Maintain a global hash table of prepared direct keys for v1 DIRECT_KEY policies.
- Prepare and refcount direct-key entries by descriptor, mode, and raw key bytes.
- Derive v1 per-file encryption keys using the file nonce as an AES-128 key over master-key blocks.
- Set up v1 file keys either directly or via derived per-file keys.

## Key APIs
- `fscrypt_put_direct_key()`
- `fscrypt_setup_v1_file_key()`
- `fscrypt_setup_v1_file_key_via_subscribed_keyrings()`

## Important Behavior
The direct-key table hashes by descriptor rather than raw key to avoid leaking secret key bytes through timing, then uses `crypto_memneq()` for constant-time raw-key comparison. Entries are scoped by superblock, descriptor, mode, and raw key and are freed when the refcount reaches zero.

The legacy v1 KDF encrypts master-key blocks with AES-128-ECB using the file nonce as the AES key. Comments explicitly note this method is nonstandard, non-extensible, and reversible if a derived key is compromised; new code should use v2 HKDF instead.

Subscribed-keyring lookup remains a fallback only for v1 policies and only after filesystem-level key lookup has failed, preventing process keyrings from overriding filesystem-level keys.

## Research Notes
This file exists to preserve v1 behavior while containing its risks. New fscrypt functionality such as v2 HKDF, per-user key claims, and hardware-wrapped keys intentionally does not route through this path.
