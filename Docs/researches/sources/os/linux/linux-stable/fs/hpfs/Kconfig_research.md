# File Research: sources/os/linux/linux-stable/fs/hpfs/Kconfig

## Purpose

Defines the `HPFS_FS` kernel configuration option.

## Behavior

`HPFS_FS` is a tristate filesystem option for OS/2 HPFS support. It depends on `BLOCK` and selects `BUFFER_HEAD` and `FS_IOMAP`. Help text documents read/write support for HPFS partitions and module name `hpfs`.

## Risks

The option enables write-capable HPFS support. It selects legacy buffer-head infrastructure and iomap support required by the implementation.
