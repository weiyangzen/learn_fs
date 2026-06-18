# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_symlink_remote.h

## Purpose

Declares the remote symlink encoding, decoding, verification, read, write, and truncate APIs.

## Main API

- `xfs_symlink_blocks`
- `xfs_symlink_hdr_set`
- `xfs_symlink_hdr_ok`
- `xfs_symlink_local_to_remote`
- `xfs_symlink_shortform_verify`
- `xfs_symlink_remote_read`
- `xfs_symlink_write_target`
- `xfs_symlink_remote_truncate`

## Research Notes

This header exposes the complete remote symlink helper surface. The implementation handles both CRC and non-CRC filesystem formats.
