# File Research: sources/os/linux/linux-stable/fs/smb/client/export.c

This file contains CIFS exportfs hooks for optional NFSD export support.

Main responsibilities:
- Under `CONFIG_CIFS_NFSD_EXPORT`, defines `cifs_export_ops`.
- Uses `generic_encode_ino32_fh` for file handle encoding.
- Provides a stub `cifs_get_parent()` that currently logs and returns `-EACCES`.

Important behavior:
- Comments document that NFS-exporting CIFS mounts requires an explicit `fsid` and the CIFS mount should use `serverino` for stable inode numbers.
- The implementation is incomplete because mandatory export operation `fh_to_dentry` is not provided here.
- Parent lookup is explicitly not implemented.

Research notes:
- This file is a placeholder/partial exportfs integration point rather than full NFSD export support.
- The comments identify a future improvement: using routines that support 64-bit inode numbers instead of default 32-bit exportfs helpers.
