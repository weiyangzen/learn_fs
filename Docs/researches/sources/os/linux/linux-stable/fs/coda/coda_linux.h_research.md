# File Research: sources/os/linux/linux-stable/fs/coda/coda_linux.h

## Purpose
Declares Linux-side Coda VFS operations, common helper APIs, and inline accessors from VFS inodes to Coda private state.

## Main Contents
- Extern operation tables for directories, files, ioctl/control, dentries, address spaces, and symlinks.
- Shared operation prototypes: open, release, permission, inode revalidation, getattr, setattr.
- Helper prototypes from `coda_linux.c`.
- Inline accessors: `ITOC()`, `coda_i2f()`, `coda_i2s()`.
- Inline `coda_flag_inode()` to set Coda inode flags under `c_lock`.

## Integration Points
Included by most Coda implementation files. It bridges VFS operation tables with Coda-specific FID and inode-private data.

## Risks And Review Focus
- `coda_flag_inode()` does not drop inode references or purge immediately; later revalidation/delete paths interpret the flags.
- Header exposes many operation tables, so signature changes must track VFS API changes consistently.
