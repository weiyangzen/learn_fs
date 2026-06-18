# File Research: sources/os/linux/linux/fs/qnx6/Makefile

## Role

Build rules for the QNX6 filesystem driver.

## Contents

- Builds `qnx6.o` under `CONFIG_QNX6FS_FS`.
- Object list: `inode.o`, `dir.o`, `namei.o`, `super_mmi.o`.
- Adds `-DDEBUG` when `CONFIG_QNX6FS_DEBUG` is enabled.

## Research Notes

The comment still says qnx4 routines, but the object list and target are QNX6-specific.
