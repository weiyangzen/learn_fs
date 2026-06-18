# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs.h

## Purpose

Defines the ABI between hostfs kernel-facing code and UML host syscall adapter code.

## API Surface

Defines `hostfs_timespec`, `hostfs_iattr`, and `hostfs_stat`, then declares wrappers for stat/access/open/dir iteration/read/write/fsync/create/setattr/symlink/unlink/mkdir/rmdir/mknod/link/readlink/rename/statfs.

## Dependencies

Includes UML OS support and generated asm offsets. Types mirror Linux inode attributes but use host-compatible scalar fields and encoded device major/minor pairs.

## Risks

This is a boundary header between VFS code and host syscall code. Layout or type mismatches can corrupt inode metadata, timestamps, or device numbers across the UML boundary.
