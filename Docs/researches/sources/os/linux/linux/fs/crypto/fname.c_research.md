# File Research: sources/os/linux/linux/fs/crypto/fname.c

## Purpose
Implements fscrypt filename encryption/decryption, no-key filename presentation and lookup, encrypted filename length calculation, SipHash dirhashing, and encrypted dentry revalidation.

## Main Elements
- Filename encryption: `fscrypt_fname_encrypt()` pads plaintext to the encrypted length, generates filename IV, and encrypts in-place into the output buffer.
- Filename decryption: `fname_decrypt()` decrypts ciphertext names and strips trailing NUL padding with `strnlen()`.
- Length calculation: `__fscrypt_fname_encrypted_size()` and `fscrypt_fname_encrypted_size()` enforce minimum 16-byte encrypted names and policy padding.
- Buffer helpers: `fscrypt_fname_alloc_buffer()` and `fscrypt_fname_free_buffer()` allocate/free buffers large enough for decrypted or no-key encoded names.
- No-key names: `struct fscrypt_nokey_name` stores dirhashes, up to 149 ciphertext bytes, and SHA-256 of the remainder; `fscrypt_fname_disk_to_usr()` base64url-encodes this when the key is unavailable.
- Lookup setup: `fscrypt_setup_filename()` prepares disk names for unencrypted dirs, keyed encrypted dirs, or keyless lookup using decoded no-key names.
- Matching: `fscrypt_match_name()` compares full disk names or validates abbreviated no-key names with SHA-256.
- Directory hash: `fscrypt_fname_siphash()` computes SipHash over plaintext names using the directory's secret dirhash key.
- Dentry validation: `fscrypt_d_revalidate()` invalidates no-key dentries once the directory key becomes available, while handling RCU lookup constraints.

## Dependencies And Integration
Works with fscrypt key setup, policy flags, skcipher content primitives from `crypto.c`, Linux base64url helpers, SHA-256, SipHash, dcache flags, and filesystem directory lookup/create paths.

## Risk Notes
No-key names must be reversible enough to find entries without exposing illegal path characters or exceeding `NAME_MAX`. Long names rely on SHA-256 collision resistance for matching. Key availability changes can make cached no-key dentries stale, so revalidation is required.
