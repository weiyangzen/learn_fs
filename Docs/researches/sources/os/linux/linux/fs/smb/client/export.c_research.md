# File Research: sources/os/linux/linux/fs/smb/client/export.c

## Purpose
Provides CIFS hooks for exportfs/NFSD export support when `CONFIG_CIFS_NFSD_EXPORT` is enabled.

## Main Interfaces
- Defines `cifs_export_ops` under `CONFIG_CIFS_NFSD_EXPORT`.
- Uses `generic_encode_ino32_fh` for file-handle encoding.
- Provides stub `cifs_get_parent()`.

## Control Flow
The only implemented parent lookup function logs a debug message and returns `-EACCES`. The comments explain that full NFS export support would require mandatory export operations such as `fh_to_dentry`, and that CIFS exports require an explicit `fsid` plus stable server inode numbers via `serverino`.

## Integration Points
Included by CIFS filesystem registration code when export support is configured. Relies on Linux exportfs helpers and CIFS inode/debug definitions.

## Risks And Review Focus
- Export support is incomplete: `get_parent()` denies access and `fh_to_dentry` is not implemented here.
- The current encoder is 32-bit inode based even though CIFS/server inode numbers may be 64-bit; comments note this could be improved.
- CIFS-as-NFS-export correctness depends on stable server inode numbers and explicit export `fsid`.
