# File Research: sources/os/linux/linux-stable/fs/crypto/fscrypt_private.h

## Summary
Private fscrypt header defining the in-kernel data structures, constants, helper accessors, and internal interfaces used by Linux filesystem encryption. It ties together on-disk encryption contexts, in-memory policies, inode encryption state, prepared keys, IV construction, HKDF domain separation, filesystem master-key lifecycle, inline-crypto support, key setup, v1 compatibility, and policy handling.

## Main Responsibilities
- Define fscrypt context versions stored on disk: `fscrypt_context_v1`, `fscrypt_context_v2`, and `union fscrypt_context`.
- Define `union fscrypt_policy` and helpers for policy size, contents/filename modes, flags, and data-unit size.
- Define `struct fscrypt_inode_info`, the per-inode encryption state cached for encrypted files.
- Define `struct fscrypt_prepared_key`, supporting both Crypto API transforms and optional blk-crypto keys.
- Define fscrypt IV representation in `union fscrypt_iv`, including DIRECT_KEY nonce and DUN array views.
- Define HKDF context byte assignments for key identifiers, per-file keys, direct keys, IV_INO_LBLK keys, dirhash keys, and inode-hash keys.
- Define master-key secret and live master-key state structures, including active/structural refcount semantics.
- Declare internal APIs implemented by `crypto.c`, `fname.c`, `hkdf.c`, `inline_crypt.c`, `keyring.c`, `keysetup.c`, `keysetup_v1.c`, and `policy.c`.

## Key Data Structures
- `struct fscrypt_inode_info`: stores the prepared encryption key, ownership flags, inline-crypto flag, data-unit bits, hashed inode number, selected mode, inode/master-key backpointers, direct-key pointer, dirhash SipHash key, inherited policy, and file nonce.
- `struct fscrypt_master_key_secret`: stores HKDF state, key type, key size, and raw or hardware-wrapped key bytes while needed.
- `struct fscrypt_master_key`: filesystem-level master-key object with RCU keyring linkage, `mk_sem`, active and structural refs, user-claim keyring, decrypted-inode list, cached per-mode prepared keys, inode-hash key, and present/removal state.
- `struct fscrypt_mode`: maps fscrypt mode numbers to user-friendly names, Crypto API cipher strings, key sizes, security strengths, IV sizes, logging state, and blk-crypto mode numbers.

## Important Behavior
The header documents the master-key state machine: present, incompletely removed, and absent. Active refs keep a key in the filesystem keyring and preserve embedded prepared keys; structural refs only preserve the object memory. This distinction lets key removal wipe secrets immediately while keeping tracking state for decrypted inodes that are still cached.

`fscrypt_is_key_prepared()` uses acquire loads paired with release stores in the key-preparation paths. This is needed because per-mode prepared keys can be published concurrently and then reused by racing inodes.

The file explicitly undefines the UAPI `FSCRYPT_MAX_KEY_SIZE` for kernel code because hardware-wrapped keys make that raw-key-specific name misleading. Kernel internals instead use raw, hardware-wrapped, and maximum-any-key size constants.

## Research Notes
This is the fscrypt internal dependency hub. The central invariants are exact context/policy sizes, domain-separated HKDF labels, master-key refcount/lifecycle rules, and the split between inode-owned per-file keys, shared per-mode keys, legacy direct keys, and hardware-wrapped blk-crypto keys.
