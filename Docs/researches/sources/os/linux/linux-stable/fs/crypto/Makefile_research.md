# File Research: sources/os/linux/linux-stable/fs/crypto/Makefile

This file defines fscrypt build composition.

Key responsibilities:
- Builds `fscrypto.o` when `CONFIG_FS_ENCRYPTION` is enabled.
- Core objects: `crypto.o`, `fname.o`, `hkdf.o`, `hooks.o`, `keyring.o`, `keysetup.o`, `keysetup_v1.o`, and `policy.o`.
- Adds `bio.o` when block support is enabled.
- Adds `inline_crypt.o` when inline encryption is enabled.

Dependencies:
- This group covers only a subset: `bio.c`, `crypto.c`, and `fname.c`.
