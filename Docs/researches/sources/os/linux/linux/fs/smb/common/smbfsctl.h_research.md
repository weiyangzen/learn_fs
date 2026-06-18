# File Research: sources/os/linux/linux/fs/smb/common/smbfsctl.h

This header defines SMB/CIFS/SMB2 FSCTL and reparse-tag constants. It documents the 32-bit FSCTL bit layout as device, access, function, and method fields.

Key contents:
- Device, access, function, and method masks for FSCTL decoding.
- Common FSCTL operation codes for DFS referrals, oplocks, sparse/zero data, reparse points, copychunk, offload read/write, snapshots, validate negotiate info, named pipes, and network interface queries.
- Reparse tags for mount points, DFS, symlinks, NFS, Azure File Sync, AF_UNIX, and WSL Linux file types.
- `IS_REPARSE_TAG_NAME_SURROGATE(tag)` helper macro.
- `SMB2_0_IOCTL_IS_FSCTL` request flag.

The file is a protocol constant catalog with no runtime logic.
