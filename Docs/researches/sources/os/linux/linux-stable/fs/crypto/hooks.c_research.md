# File Research: sources/os/linux/linux-stable/fs/crypto/hooks.c

## Summary
Implements VFS-facing fscrypt hooks for higher-level filesystem operations. It enforces key availability and policy consistency for open/link/rename/lookup/readdir/setattr/setflags, and handles encrypted symlink sizing, encryption, decryption or no-key presentation, caching, and `st_size` reporting.

## Main Responsibilities
- Require encryption keys before opening encrypted regular files.
- Enforce that encrypted directory trees do not contain children with incompatible policies.
- Reject hard links and renames involving no-key dentries or cross-policy moves.
- Prepare lookup/readdir operations that may proceed without keys for deletion-oriented workflows.
- Require the file key before size-changing `setattr`.
- Derive directory hash keys when enabling casefolding on encrypted v2-policy directories.
- Prepare encrypted symlink disk sizes and encrypt symlink targets.
- Return decrypted symlink targets when the key is present or no-key encoded targets when absent.
- Override encrypted symlink `st_size` with the size userspace actually sees.

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
`fscrypt_file_open()` first requires the target key, then uses a lightweight RCU parent check to avoid unnecessary parent dentry refcounting when the parent is unencrypted. It only takes a parent reference and compares policies when the parent may be encrypted.

Lookup preparation treats an unavailable key differently from a hard failure. No-key names are permitted for operations that allow deletion without a key, while link and rename reject no-key dentries with `-ENOKEY`.

Encrypted symlinks store a little-endian ciphertext length prefix for historical reasons and include a trailing NUL in the stored length even though the ciphertext does not semantically require one. Decrypted symlink targets are cached in `inode->i_link` with release semantics; no-key encodings are not cached because adding the key would make them stale.

## Research Notes
This file is the fscrypt enforcement layer closest to VFS operations. It relies on key setup from `keysetup.c`, policy comparison from `policy.c`, filename helpers, and the VFS symlink `i_link` cache contract.
