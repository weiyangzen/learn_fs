# File Research: sources/os/linux/linux-stable/fs/crypto/Kconfig

This file declares fscrypt build options.

Key responsibilities:
- Defines `CONFIG_FS_ENCRYPTION` for per-file filesystem encryption.
- Selects crypto primitives and key support needed by fscrypt core.
- Defines `CONFIG_FS_ENCRYPTION_ALGS`, a tristate option filesystems select to pull default encryption algorithms.
- Defines `CONFIG_FS_ENCRYPTION_INLINE_CRYPT` for inline encryption hardware support.

Dependencies:
- Filesystems such as ext4, f2fs, ubifs, and cephfs use this feature.
- Inline crypt depends on `FS_ENCRYPTION && BLK_INLINE_ENCRYPTION`.

Risks and invariants:
- `FS_ENCRYPTION_ALGS` intentionally pulls generic implementations only; optimized arch implementations remain separate.
- Non-default modes such as Adiantum may require explicit crypto API configuration.
