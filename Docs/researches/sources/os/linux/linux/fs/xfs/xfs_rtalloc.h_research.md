# File Research: sources/os/linux/linux/fs/xfs/xfs_rtalloc.h

## Role

Header for realtime allocation and grow/mount interfaces.

## Main Contents

When `CONFIG_XFS_RT` is enabled, declares:

- `xfs_rtmount_readsb` and `xfs_rtmount_freesb`.
- `xfs_rtmount_init`.
- `xfs_rtmount_inodes` and `xfs_rtunmount_inodes`.
- `xfs_growfs_rt`.
- `xfs_rtalloc_reinit_frextents`.
- `xfs_growfs_check_rtgeom`.

When realtime support is disabled, provides stubs returning success for no-RT cases or `-ENOSYS`/warnings for unsupported realtime mounts.

Always declares `xfs_rtallocate_rtgs`, the rtgroup allocation entry point used by bmap allocation.

## Important Note

The disabled-RT stub section contains a macro typo-like reference in `xfs_rtmount_inodes(m)` using `mp` instead of `m`; this is source as read and may be covered by build configuration paths elsewhere.

## Dependencies

Forward declares mount and transaction types and exposes realtime allocation types used by bmap and growfs code.
