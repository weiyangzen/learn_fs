# File Research: sources/os/linux/linux-stable/fs/hugetlbfs/Makefile

This Makefile builds hugetlbfs when `CONFIG_HUGETLBFS` is enabled.

Key responsibilities:
- Adds `hugetlbfs.o` to the build for `CONFIG_HUGETLBFS`.
- Defines `hugetlbfs-objs := inode.o`, making `inode.c` the implementation unit for the hugetlbfs object.

Research notes:
- Despite the legacy comment mentioning ramfs routines, the build rule is narrowly scoped to hugetlbfs.
