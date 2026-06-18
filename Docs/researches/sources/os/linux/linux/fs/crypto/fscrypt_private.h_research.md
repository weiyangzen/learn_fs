# File Research: sources/os/linux/linux/fs/crypto/fscrypt_private.h

## Summary
Private fscrypt header defining the in-kernel representations, constants, helper accessors, and internal function interfaces used by Linux filesystem encryption. It bridges UAPI policies/contexts, inode encryption state, master-key state, crypto mode metadata, HKDF contexts, inline-crypto integration, keyring management, key setup, v1 compatibility, and policy operations.

## Main Responsibilities
- Define fscrypt context versions stored on disk: `fscrypt_context_v1`, `fscrypt_context_v2`, and `union fscrypt_context`.
- Define in-kernel policy wrapper `union fscrypt_policy` and helpers for policy size, modes, flags, and data-unit size.
- Define per-inode encryption state in `struct fscrypt_inode_info`.
- Define prepared-key state in `struct fscrypt_prepared_key`, supporting Crypto API transforms and optional blk-crypto keys.
- Define IV layout via `union fscrypt_iv`, including file data-unit index and DIRECT_KEY nonce use.
- Define HKDF context labels that domain-separate fscrypt KDF outputs.
- Define master-key secret and live master-key state structures.
- Declare internal APIs implemented across `crypto.c`, `fname.c`, `hkdf.c`, `inline_crypt.c`, `keyring.c`, `keysetup.c`, `keysetup_v1.c`, and `policy.c`.

## Key Data Structures
- `struct fscrypt_inode_info`: cached key material and policy for an inode, including selected mode, nonce, data-unit size, master-key backpointer, direct-key pointer, directory SipHash key, and inline-crypto flag.
- `struct fscrypt_master_key_secret`: KDF state, raw or hardware-wrapped key bytes, size, and hardware-wrapped flag.
- `struct fscrypt_master_key`: filesystem-level master key object with active/structural refs, present/removal state, per-user keyring, decrypted inode list, cached per-mode keys, and inode-hash key.
- `struct fscrypt_mode`: maps fscrypt mode numbers to friendly names, Crypto API cipher strings, key sizes, security strength, IV size, logging state, and blk-crypto mode numbers.

## Important Behavior
The header documents the master-key state model: `PRESENT`, `INCOMPLETELY_REMOVED`, and `ABSENT`. Active refs keep a key in the filesystem keyring and keep prepared subkeys alive; structural refs keep the object memory alive. This distinction is central to safe key removal while decrypted inodes may still be cached.

`fscrypt_is_key_prepared()` uses acquire loads paired with release stores in key preparation paths, because per-mode keys can be published concurrently. Inline crypto is abstracted so non-inline builds compile to stubs that reject hardware-wrapped keys and use Crypto API transforms.

The file also intentionally undefines misleading `FSCRYPT_MAX_KEY_SIZE` for kernel code, replacing it with raw, hardware-wrapped, and maximum-any-key size constants.

## Research Notes
This header is the dependency hub for fscrypt internals. The most important invariants are context/policy version sizing, domain-separated HKDF labels, master-key lifecycle/refcount rules, and the separation between inode-owned per-file keys, shared per-mode keys, and legacy direct keys.
