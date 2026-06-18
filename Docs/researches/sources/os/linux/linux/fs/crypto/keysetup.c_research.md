# File Research: sources/os/linux/linux/fs/crypto/keysetup.c

## Summary
Implements fscrypt key setup for encrypted inodes. It selects encryption modes, allocates Crypto API transforms or blk-crypto keys, derives per-file and per-mode keys, handles v2 policy KDFs, initializes per-inode encryption info, prepares new encrypted inodes, and tears encryption info down during inode eviction/free/drop.

## Main Responsibilities
- Define supported fscrypt modes and their cipher strings, key sizes, IV sizes, security strengths, and blk-crypto mappings.
- Select contents or filename encryption mode based on inode type.
- Allocate and initialize Crypto API skcipher transforms.
- Prepare and destroy `fscrypt_prepared_key` objects.
- Derive shared per-mode keys with HKDF for DIRECT_KEY and IV_INO_LBLK policies.
- Derive per-file keys with HKDF for standard v2 policies.
- Derive SipHash keys for casefolded directory hashes and inode-number hashing.
- Set up v2 keys, including hardware-wrapped key restrictions.
- Find master keys and fall back to legacy v1 subscribed keyrings when needed.
- Allocate, publish, and race-resolve `fscrypt_inode_info`.
- Prepare new encrypted inodes before filesystem transactions.
- Free inode encryption info and cached symlink targets.
- Tell the VFS to drop inodes whose master key was removed.

## Key APIs
- `fscrypt_prepare_key()`
- `fscrypt_destroy_prepared_key()`
- `fscrypt_set_per_file_enc_key()`
- `fscrypt_derive_dirhash_key()`
- `fscrypt_hash_inode_number()`
- `fscrypt_get_encryption_info()`
- `fscrypt_prepare_new_inode()`
- `fscrypt_put_encryption_info()`
- `fscrypt_free_inode()`
- `fscrypt_drop_inode()`

## Important Behavior
Per-mode prepared keys are shared under a global setup mutex and published with release stores so concurrent inodes can acquire them safely. Standard v2 policies derive per-file encryption keys from master-key HKDF and the inode nonce. DIRECT_KEY v2 derives per-mode keys rather than reusing master keys directly. `IV_INO_LBLK_64` and `IV_INO_LBLK_32` derive per-mode keys with filesystem UUID in HKDF info.

`IV_INO_LBLK_32` also derives an inode-hash SipHash key on demand. Existing inodes hash immediately; new inodes may not have an inode number yet, so hashing can be delayed until `fscrypt_set_context()`.

`fscrypt_get_encryption_info()` treats missing keys as a nonfatal result and requires callers to check `fscrypt_has_encryption_key()`. It can also treat unsupported contexts or algorithms as nonfatal when operations need to proceed for deletion.

Publishing `fscrypt_inode_info` uses `cmpxchg_release()` because multiple tasks can race to set up the same existing inode. The winner links the inode into the master key’s decrypted-inode list and takes an active key ref.

## Research Notes
This file is the central bridge between policy, master-key storage, and actual per-inode encryption capability. Its key invariants are KDF context selection, master-key size validation, safe publication of shared keys and inode info, and cleanup coordination with key removal.
