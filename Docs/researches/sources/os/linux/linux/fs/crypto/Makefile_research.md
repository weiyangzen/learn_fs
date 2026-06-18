# File Research: sources/os/linux/linux/fs/crypto/Makefile

## Purpose
Builds the fscrypt support library.

## Main Elements
- Core `fscrypto.o` objects: `crypto.o`, `fname.o`, `hkdf.o`, `hooks.o`, `keyring.o`, `keysetup.o`, `keysetup_v1.o`, and `policy.o`.
- Adds `bio.o` when `CONFIG_BLOCK` is enabled.
- Adds `inline_crypt.o` when `CONFIG_FS_ENCRYPTION_INLINE_CRYPT` is enabled.

## Dependencies And Integration
Defines which fscrypt components are linked for encryption policy/key/content/name/block integration.

## Risk Notes
Filesystems using block-device fscrypt helpers depend on `bio.o`; inline crypto hooks are feature-gated separately.
