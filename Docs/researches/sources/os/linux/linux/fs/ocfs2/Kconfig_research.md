# File Research: sources/os/linux/linux/fs/ocfs2/Kconfig

## Role

Declares build-time configuration options for the OCFS2 clustered filesystem and its clustering/debug/statistics features.

## Major Options

- `OCFS2_FS`:
  - Main OCFS2 filesystem support.
  - Depends on `INET`, `SYSFS`, and `CONFIGFS_FS`.
  - Selects buffer heads, JBD2, CRC32, quota support, POSIX ACL filesystem support, and legacy direct I/O.
  - Help text describes OCFS2 as a general-purpose extent-based shared-disk cluster filesystem, with 64-bit inode numbers and extending metadata groups.
- `OCFS2_FS_O2CB`:
  - Kernelspace O2CB clustering support.
  - Depends on `OCFS2_FS`.
  - Defaults to `y`.
  - Runtime selectable.
- `OCFS2_FS_USERSPACE_CLUSTER`:
  - Userspace clustering with fs/dlm.
  - Depends on `OCFS2_FS && DLM`.
  - Defaults to `y`.
  - Runtime selectable.
- `OCFS2_FS_STATS`:
  - Debugfs-backed statistics.
  - Depends on `OCFS2_FS && DEBUG_FS`.
  - Defaults to `y`.
- `OCFS2_DEBUG_MASKLOG`:
  - Extensive masklog logging.
  - Depends on `OCFS2_FS`.
  - Defaults to `y`.
- `OCFS2_DEBUG_FS`:
  - Expensive consistency checks.
  - Depends on `OCFS2_FS`.
  - Defaults to `n`.

## Important Invariants

- POSIX ACL support is selected by the main OCFS2 option, so OCFS2 ACL code is expected to be available when the filesystem is enabled.
- Clustering backend choice is compiled separately but runtime selectable.
- Expensive debug checks are intentionally opt-in.

## Dependencies

- Kernel Kconfig system.
- OCFS2 tooling and docs are referenced in help text.

## Notes For Future Work

- Because `OCFS2_FS_O2CB` and `OCFS2_FS_USERSPACE_CLUSTER` both default to enabled, builds may include both cluster stacks unless downstream configs trim them.
