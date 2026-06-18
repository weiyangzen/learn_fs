# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr_system.c

OS-backed xattr restoration for `unsquashfs` builds with xattr system support.

Key function:
- `write_xattr(pathname, xattr)` loads the inode's xattr list, applies include/exclude regex filters, and writes each permitted xattr using `lsetxattr()`.

Important behavior:
- Non-root users may write only `user.*` namespace xattrs; first non-user failure emits guidance and suppresses repeated messages.
- `ENOTSUP` disables further xattr output after warning that the destination filesystem does not support xattrs.
- `ENOSPC`/`EDQUOT` messages are capped by `NOSPACE_MAX` to avoid repeated per-file noise.
- Filesystem corruption is fatal if the inode xattr index exceeds `sBlk.xattr_ids`.
- Strict/ignore behavior is routed through `EXIT_UNSQUASH_STRICT()` and `EXIT_UNSQUASH_IGNORE()`.

Uses `xattr_compat.h` to normalize Linux/BSD/macOS no-follow xattr APIs.
