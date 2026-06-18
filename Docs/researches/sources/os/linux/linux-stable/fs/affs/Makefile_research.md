# File Research: sources/os/linux/linux-stable/fs/affs/Makefile
- Purpose: Builds the AFFS filesystem module/object.
- Main object: `affs.o` is built under `CONFIG_AFFS_FS`.
- Component objects: `super.o`, `namei.o`, `inode.o`, `file.o`, `dir.o`, `amigaffs.o`, `bitmap.o`, and `symlink.o`.
- Integration: This file shows `amigaffs.c` is a shared helper unit rather than the whole filesystem implementation.
