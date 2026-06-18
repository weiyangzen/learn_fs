# File Research: sources/os/linux/linux/fs/crypto/hooks.c

## Summary
Implements fscrypt hooks used by higher-level filesystem operations. It enforces key availability and policy consistency for open/link/rename/lookup/setattr/setflags, and handles encrypted symlink sizing, encryption, decryption/no-key presentation, and `st_size` reporting.

## Main Responsibilities
- Require encryption keys before opening encrypted regular files.
- Enforce that encrypted directory trees do not contain children with incompatible policies.
- Prepare link and rename operations, rejecting no-key names and cross-policy moves.
- Prepare lookup/readdir paths that may need to operate without keys.
- Prepare size-changing setattr operations by requiring the file key.
- Support casefold flag changes on encrypted directories by deriving dirhash keys.
- Prepare, encrypt, read, cache, and stat encrypted symlink targets.

## Key APIs
- `fscrypt_file_open()`
- `__fscrypt_prepare_link()`
- `__fscrypt_prepare_rename()`
- `__fscrypt_prepare_lookup()`
- `fscrypt_prepare_lookup_partial()`
- `__fscrypt_prepare_readdir()`
- `__fscrypt_prepare_setattr()`
- `fscrypt_prepare_setflags()`
- `fscrypt_prepare_symlink()`
- `__fscrypt_encrypt_symlink()`
- `fscrypt_get_symlink()`
- `fscrypt_symlink_getattr()`

## Important Behavior
`fscrypt_file_open()` first requires the target key, then cheaply checks under RCU whether the parent is unencrypted. Only if needed does it take a parent dentry reference and compare policies. This avoids expensive parent refcounting for the common unencrypted-parent case.

Lookup preparation distinguishes “key unavailable” from hard failure. No-key names are allowed for deletion-oriented operations, but link and rename reject them with `-ENOKEY`.

Encrypted symlinks store a little-endian ciphertext length prefix for historical reasons and count a trailing NUL in the stored length even though ciphertext does not semantically need one. `fscrypt_get_symlink()` decrypts when the key exists, otherwise returns the no-key encoded target. Decrypted targets are cached in `inode->i_link` with release semantics; no-key encodings are not cached because they become stale when the key is added.

## Research Notes
This file is the VFS-facing enforcement layer. It depends on policy comparison from `policy.c`, key setup from `keysetup.c`, filename encryption helpers, and the inode `i_link` cache behavior expected by path lookup.
