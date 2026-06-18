# File Research: sources/os/linux/linux/fs/crypto/keysetup_v1.c

## Summary
Implements compatibility support for legacy fscrypt v1 encryption policies. It supports the original AES-128-ECB-based per-file KDF, process-subscribed keyring lookup, and legacy DIRECT_KEY handling through a global direct-key table.

## Main Responsibilities
- Search current task subscribed keyrings for legacy `logon` keys by descriptor.
- Validate legacy key payload size and minimum key size.
- Derive v1 per-file keys using the historical AES-ECB KDF.
- Support v1 DIRECT_KEY by preparing and sharing direct master-key transforms.
- Maintain a hash table of direct keys keyed by descriptor and mode, while comparing raw key bytes with constant-time comparison.
- Fall back to filesystem legacy key prefixes when provided.

## Key APIs
- `fscrypt_setup_v1_file_key()`
- `fscrypt_setup_v1_file_key_via_subscribed_keyrings()`
- `fscrypt_put_direct_key()`

## Important Behavior
Legacy v1 non-DIRECT_KEY derivation encrypts chunks of the raw master key using AES-128-ECB with the inode nonce as the AES key. The file comments explicitly call this nonstandard, nonextensible, uneven in entropy distribution, and reversible if a derived key is compromised.

For DIRECT_KEY, the file uses a global `fscrypt_direct_keys` table so files sharing the same descriptor, mode, and raw key can share a prepared key. The hash table does not key by raw key to avoid leaking secret-dependent timing through hashing; raw keys are compared with `crypto_memneq()`.

Process-subscribed keyring lookup is intentionally legacy fallback and should not override filesystem-level keys.

## Research Notes
This is compatibility code for deprecated v1 policy behavior. Newer security properties, user accounting, HKDF, and key removal semantics live in v2 filesystem-level keyring paths.
