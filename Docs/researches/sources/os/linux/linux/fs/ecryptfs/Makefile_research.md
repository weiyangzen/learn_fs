# File Research: sources/os/linux/linux/fs/ecryptfs/Makefile

## Role

`fs/ecryptfs/Makefile` defines object composition for the eCryptfs kernel module.

## Build Composition

`obj-$(CONFIG_ECRYPT_FS) += ecryptfs.o` builds eCryptfs when enabled.

The base module includes dentry, file, inode, main, super, mmap, read/write, crypto, keystore, kthread, and debug objects.

When `CONFIG_ECRYPT_FS_MESSAGING` is enabled, messaging and miscdev objects are added.

## Research Notes

Read completely. This file is build glue and has no runtime logic.
