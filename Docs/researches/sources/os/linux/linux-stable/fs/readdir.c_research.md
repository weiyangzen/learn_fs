# File Research: sources/os/linux/linux-stable/fs/readdir.c

## Purpose
Implements VFS directory iteration wrappers and user ABI syscalls for reading directory entries.

## Main Responsibilities
- `iterate_dir()`: validates directory iteration support, checks permissions, takes shared inode lock, calls `iterate_shared`, updates `f_pos`, and emits access notifications.
- `wrap_directory_iterator()`: adapts old filesystems needing exclusive inode locking by temporarily upgrading from shared to write lock and downgrading afterward.
- `verify_dirent_name()`: rejects invalid directory entry names with zero/negative length, length at or above `PATH_MAX`, or embedded `/`.
- Implements old `readdir`, `getdents`, `getdents64`, and compat variants.

## ABI Writers
- `fillonedir()`: old one-entry ABI.
- `filldir()`: native `linux_dirent`.
- `filldir64()`: native `linux_dirent64`.
- `compat_fillonedir()` and `compat_filldir()`: compat ABI versions.

The fill callbacks:
- verify names,
- detect inode number overflow for narrower ABI fields,
- handle record alignment and buffer space,
- copy names and metadata to userspace with unsafe user access helpers,
- update previous record offsets when final position is known.

## Edge Cases
- Signal interruption is avoided for the first emitted entry but can stop after at least one record unless `FILLDIR_FLAG_NOINTR` is set.
- Dead directories return `-ENOENT`.
- Corrupt names are treated as hard errors.
