# File Research: sources/os/linux/linux/fs/crypto/Kconfig

## Purpose
Defines filesystem encryption and optional inline encryption build configuration.

## Main Elements
- `FS_ENCRYPTION`: core per-file encryption support, selecting crypto, skcipher, AES/SHA libraries, and keys.
- `FS_ENCRYPTION_ALGS`: tristate algorithm bundle for default fscrypt modes, selecting AES, CBC, CTS, and XTS.
- `FS_ENCRYPTION_INLINE_CRYPT`: optional fscrypt inline crypto support depending on block inline encryption.

## Dependencies And Integration
Used by filesystems such as ext4, f2fs, ubifs, and cephfs to enable fscrypt support and required algorithms.

## Risk Notes
The default algorithm option does not select every possible fscrypt algorithm or architecture-optimized implementation; deployments using non-default modes must enable those crypto API algorithms separately.
