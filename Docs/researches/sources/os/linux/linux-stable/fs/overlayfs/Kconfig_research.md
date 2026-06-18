# File Research: sources/os/linux/linux-stable/fs/overlayfs/Kconfig

## Scope

This Kconfig file defines overlayfs build selection and default feature toggles for redirects, redirect following, index, NFS export, xino inode mapping, metacopy, and debug checks.

## Configuration Options

- `OVERLAY_FS`: tristate overlay filesystem support; selects `FS_STACK` and `EXPORTFS`.
- `OVERLAY_FS_REDIRECT_DIR`: default-on behavior for directory rename redirects when enabled.
- `OVERLAY_FS_REDIRECT_ALWAYS_FOLLOW`: default `y`; preserves backward-compatible redirect following even when redirects are otherwise off.
- `OVERLAY_FS_INDEX`: default feature for index directory mapping of lower inodes to upper inodes, preserving lower hardlinks on copy-up.
- `OVERLAY_FS_NFS_EXPORT`: depends on overlayfs index and not metacopy; defaults NFS export support.
- `OVERLAY_FS_XINO_AUTO`: 64-bit-only default for automatic inode number mapping using high bits.
- `OVERLAY_FS_METACOPY`: metadata-only copy-up default; selects redirect-dir support.
- `OVERLAY_FS_DEBUG`: enables extra debugging checks.

## Behavior And Tradeoffs

- Redirect, index, NFS export, and metacopy options are explicitly documented as not backward compatible with older kernels that do not understand the corresponding overlay metadata.
- NFS export creates a fuller index and may add mount-time verification overhead.
- XINO improves unified inode numbering at the cost of possible 32-bit inode compatibility issues for applications.
- Metacopy defers data copy-up until write open, improving metadata-heavy workloads but interacting with redirect and NFS export constraints.

## Dependencies

- These options are consumed by overlayfs parameter defaults and compile-time conditionals across the overlayfs implementation.
- `OVERLAY_FS_NFS_EXPORT` depends on `OVERLAY_FS_INDEX` and conflicts with `OVERLAY_FS_METACOPY`.

## Risks And Invariants

- Default-enabled incompatible metadata features can make mounts behave unexpectedly on older kernels.
- The Kconfig dependency graph prevents enabling NFS export by default with metacopy because that combination is not supported by this configuration.
