# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42.h

## Purpose
NFSv4.2-specific internal declarations and small helpers.

## Constants
- `PNFS_LAYOUTSTATS_MAXDEV` is set to 4, limiting layoutstats devices per compound.
- `READ_PLUS_SCRATCH_SIZE` is set to 16.

## Declared NFSv4.2 Procedures
Under `CONFIG_NFS_V4_2`:
- Space management:
  - `nfs42_proc_allocate()`
  - `nfs42_proc_deallocate()`
  - `nfs42_proc_zero_range()`
- Copy/clone/seek:
  - `nfs42_proc_copy()`
  - `nfs42_proc_clone()`
  - `nfs42_proc_llseek()`
  - `nfs42_proc_copy_notify()`
- pNFS reporting:
  - `nfs42_proc_layoutstats_generic()`
  - `nfs42_proc_layouterror()`
- Extended attributes:
  - `nfs42_proc_getxattr()`
  - `nfs42_proc_setxattr()`
  - `nfs42_proc_listxattrs()`
  - `nfs42_proc_removexattr()`

## Inline Helpers
- `nfs42_files_from_same_server(struct file *in, struct file *out)`
  - Compares major server owner IDs of input/output NFS clients.
  - Used to decide whether server-side operations can treat two files as same-server.
- `nfs42_listxattr_xdrsize(u32 buflen)`
  - Computes an upper-bound XDR buffer size for listxattr output.
  - Assumes worst case of many small `user.x` names and rounds to 4-byte alignment.

## Research Notes
This header exposes v4.2 feature entry points but does not implement them. The listxattr sizing helper encodes an important wire-buffer bound used by v4.2 xattr code.
