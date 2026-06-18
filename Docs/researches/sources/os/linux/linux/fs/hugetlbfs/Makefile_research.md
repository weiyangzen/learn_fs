# File Research: sources/os/linux/linux/fs/hugetlbfs/Makefile

Small kbuild file for hugetlbfs.

Behavior:
- Builds `hugetlbfs.o` when `CONFIG_HUGETLBFS` is enabled.
- The composite object contains only `inode.o`.

Despite the comment saying “linux ramfs routines”, this directory builds hugetlbfs. Functional risk is low; changes here affect whether the hugetlbfs implementation is linked into the kernel.
