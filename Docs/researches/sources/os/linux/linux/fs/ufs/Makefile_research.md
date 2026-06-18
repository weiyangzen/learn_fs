# File Research: sources/os/linux/linux/fs/ufs/Makefile

Purpose: build rules for the Linux UFS filesystem module.

Key contents:
- Builds `ufs.o` when `CONFIG_UFS_FS` is enabled.
- Links `balloc.o`, `cylinder.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `namei.o`, `super.o`, and `util.o`.
- Adds `-DDEBUG` when `CONFIG_UFS_DEBUG` is enabled.

Integration:
- The files in this group are core components of the module; `namei.c`, `super.c`, and `util.c` are referenced here but not part of this work item.

Risks and invariants:
- Debug behavior is compile-time gated.
