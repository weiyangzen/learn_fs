# File Research: sources/os/linux/linux-stable/fs/ufs/Makefile

## Summary
Builds the Linux UFS filesystem object from allocator, cylinder, directory, file, inode, namei, superblock, and utility sources.

## Main Responsibilities
- Links `ufs.o` when `CONFIG_UFS_FS` is enabled.
- Includes `balloc.o`, `cylinder.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `namei.o`, `super.o`, and `util.o`.
- Adds `-DDEBUG` when `CONFIG_UFS_DEBUG` is enabled.

## Risks
The object list is tightly coupled: directory/namei code depends on inode block mapping, allocator code depends on cylinder caches and util helpers, and superblock setup supplies UFS variant flags consumed everywhere.
