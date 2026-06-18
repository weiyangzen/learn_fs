# File Research: sources/local-fs/btrfs-linux/fs/btrfs/verity.h

Declares Btrfs fs-verity integration points and provides stubs when fs-verity support is disabled.

Key declarations:
- With `CONFIG_FS_VERITY`, exports `btrfs_verityops`, `btrfs_drop_verity_items()`, and `btrfs_get_verity_descriptor()`.
- Without `CONFIG_FS_VERITY`, `btrfs_drop_verity_items()` is an inline no-op returning `0`, and `btrfs_get_verity_descriptor()` returns `-EPERM`.

Core mechanics:
- The header includes `<linux/fsverity.h>` only for fs-verity builds and `<linux/errno.h>` for stub builds.
- It forward-declares `struct inode` and `struct btrfs_inode` to keep dependencies minimal.

Important invariants:
- Callers can invoke `btrfs_drop_verity_items()` unconditionally; behavior compiles to a no-op when fs-verity is unavailable.
- Descriptor access is explicitly denied when fs-verity is not configured.

Filesystem relevance:
- This header is the compile-time boundary between Btrfs core inode/orphan paths and optional fs-verity support.

Notable risks:
- Build-configuration behavior differs: cleanup calls silently succeed without fs-verity, while descriptor reads fail with permission-style error.
