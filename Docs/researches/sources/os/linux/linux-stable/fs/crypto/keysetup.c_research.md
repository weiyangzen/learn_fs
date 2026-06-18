# File Research: sources/os/linux/linux-stable/fs/crypto/keysetup.c

## Summary
Implements fscrypt key setup for encrypted inodes. It defines supported encryption modes, selects contents or filename encryption mode by inode type, prepares Crypto API or blk-crypto keys, derives per-file and per-mode keys, handles v2 policy KDFs and hardware-wrapped restrictions, publishes per-inode encryption info, prepares new encrypted inodes, and tears encryption state down during inode eviction/free/drop.

## Main Responsibilities
- Define `fscrypt_modes[]` for AES-XTS, AES-CBC-CTS, AES-CBC-ESSIV, SM4, Adiantum, and AES-HCTR2.
- Select contents encryption for regular files and filename encryption for directories/symlinks.
- Allocate and initialize synchronous skcipher transforms for filesystem-layer crypto.
- Prepare and destroy `fscrypt_prepared_key` objects.
- Derive shared per-mode keys for DIRECT_KEY and IV_INO_LBLK policies.
- Derive per-file keys for default v2 policies.
- Derive SipHash keys for casefolded directory hashes and inode-number hashing.
- Set up v2 file keys, including hardware-wrapped key constraints.
- Locate master keys in the filesystem keyring or fall back to legacy subscribed keyrings for v1 policies.
- Allocate, publish, and race-resolve `fscrypt_inode_info`.
- Prepare new encrypted inodes before filesystem transactions.
- Free inode encryption info and cached symlink targets.
- Tell VFS drop-inode logic to evict inodes whose master key has been removed.

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
Mode setup logs the actual Crypto API implementation the first time each mode is used, helping diagnose unexpected acceleration or fallback choices. It forbids weak keys through Crypto API flags and verifies transform IV sizes against fscrypt mode metadata.

Per-mode keys are shared under the master key and are protected by `fscrypt_mode_key_setup_mutex`; release/acquire publication lets racing tasks safely reuse them. V2 DIRECT_KEY and IV_INO_LBLK policies derive mode keys with HKDF rather than using master keys directly.

Hardware-wrapped keys are accepted only for v2 IV_INO_LBLK policies and require inline crypto for regular-file contents. The wrapped key is passed to blk-crypto for contents encryption, while the hardware-derived software secret is used for HKDF-derived non-contents material.

`fscrypt_setup_encryption_info()` publishes `fscrypt_inode_info` with `cmpxchg_release()` because multiple tasks can race to initialize an existing inode. The winner links the inode into the master key's decrypted-inode list and takes an active ref; losers clean up their temporary key material.

## Research Notes
This file is the bridge between policy/keyring state and per-inode usable encryption state. The main invariants are mode compatibility, KDF context separation, safe publication of shared keys and inode info, and accurate active-ref accounting for key removal.
