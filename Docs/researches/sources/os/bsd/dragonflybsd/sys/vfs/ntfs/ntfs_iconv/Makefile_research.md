# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/Makefile

This Makefile builds the `ntfs_iconv` kernel module from `ntfs_iconv.c`.

The module is separate from the base `ntfs` module and provides optional character-set conversion support through the kernel iconv framework.

Research notes: the parent NTFS Makefile includes this directory as a submodule.
