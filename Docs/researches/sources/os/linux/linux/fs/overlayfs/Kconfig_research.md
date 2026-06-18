# File Research: sources/os/linux/linux/fs/overlayfs/Kconfig

## Role

Defines Linux kernel configuration options for OverlayFS and its optional features.

## Main Options

- `OVERLAY_FS`: tristate core overlay filesystem support; selects `FS_STACK` and `EXPORTFS`.
- `OVERLAY_FS_REDIRECT_DIR`: enables redirect directory support by default.
- `OVERLAY_FS_REDIRECT_ALWAYS_FOLLOW`: follows redirects even when redirect support is disabled, defaulting to `y` for compatibility.
- `OVERLAY_FS_INDEX`: enables inode index by default to preserve lower hardlink identity across copy-up.
- `OVERLAY_FS_NFS_EXPORT`: enables NFS export support by default; depends on index and excludes metacopy.
- `OVERLAY_FS_XINO_AUTO`: enables automatic inode-number mapping on 64-bit systems.
- `OVERLAY_FS_METACOPY`: enables metadata-only copy-up by default and selects redirect-dir support.
- `OVERLAY_FS_DEBUG`: enables extra debug checks.

## Compatibility Notes

Several options warn that on-disk metadata features such as redirects, index, NFS export index, and metacopy are not backward compatible with kernels that do not understand them.

## Dependencies

These config choices feed mount defaults and compile-time feature availability across OverlayFS source files.

## Research Notes

The file documents the operational tradeoffs of feature defaults: compatibility and performance versus stronger identity/export semantics.
