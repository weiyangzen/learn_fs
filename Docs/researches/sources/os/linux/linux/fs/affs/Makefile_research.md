# File Research: sources/os/linux/linux/fs/affs/Makefile

Defines AFFS module object composition.

Key behavior:
- Builds `affs.o` when `CONFIG_AFFS_FS` is enabled.
- Combines:
  - `super.o`
  - `namei.o`
  - `inode.o`
  - `file.o`
  - `dir.o`
  - `amigaffs.o`
  - `bitmap.o`
  - `symlink.o`
- Contains a commented debug compiler flag.

Important interactions:
- The files researched in this group are shared support pieces for the complete AFFS module.
