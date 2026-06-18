# File Research: sources/os/linux/linux/fs/coda/coda_linux.h

Main Linux-side internal Coda header.

Contains:
- `pr_fmt` setup for module-prefixed logging.
- Includes for kernel memory, wait, VFS, and `coda_fs_i.h`.
- Extern declarations for inode/file/dentry/address-space operations.
- Shared operation declarations: open, release, permission, revalidate, getattr, setattr.
- Helper declarations from `coda_linux.c`: FID formatting, control-name detection, inode/vattr conversion, flag conversion.

Inline helpers:
- `ITOC()`: VFS inode to `struct coda_inode_info`.
- `coda_i2f()`: inode to Coda FID.
- `coda_i2s()`: inode to formatted FID string.
- `coda_flag_inode()`: sets Coda inode flags under `c_lock`, ignoring null inode.

Role:
- Central include for Coda implementation files needing Linux/VFS glue and Coda-private state access.
