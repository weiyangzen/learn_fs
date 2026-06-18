# File Research: sources/os/linux/linux-stable/fs/ocfs2/Kconfig

Purpose: Kconfig definitions for building OCFS2 and its clustering/debug options.

Key contents:
- `OCFS2_FS`: tristate main OCFS2 filesystem, depending on `INET`, `SYSFS`, and `CONFIGFS_FS`; selects buffer heads, JBD2, CRC32, quota support, POSIX ACLs, and legacy direct I/O.
- `OCFS2_FS_O2CB`: kernelspace O2CB clustering support, depending on `OCFS2_FS`, default enabled.
- `OCFS2_FS_USERSPACE_CLUSTER`: userspace clustering via fs/dlm, depending on `OCFS2_FS && DLM`, default enabled.
- `OCFS2_FS_STATS`: optional debugfs-backed statistics, depending on `OCFS2_FS && DEBUG_FS`, default enabled.
- `OCFS2_DEBUG_MASKLOG`: optional extensive logging/masklog support, depending on `OCFS2_FS`, default enabled.
- `OCFS2_DEBUG_FS`: optional expensive consistency checks for debugging, default disabled.

Important invariants:
- POSIX ACL support is selected unconditionally by `OCFS2_FS`.
- Both clustering stacks are build-time selectable but described as runtime selectable.
- Expensive debug checks are intentionally opt-in.

Dependencies:
- Coordinates build inclusion with the Makefile and broader kernel options for configfs/sysfs/networking/DLM/debugfs/quota/JBD2.
