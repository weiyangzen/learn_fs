# File Research: sources/os/linux/linux/fs/qnx4/Makefile

## Role

Build rules for the QNX4 filesystem driver.

## Contents

- Builds `qnx4.o` under `CONFIG_QNX4FS_FS`.
- Object list: `inode.o`, `dir.o`, `namei.o`, `bitmap.o`.

## Research Notes

The driver is small and split into mount/inode/block mapping, directory iteration, lookup, and free-block counting.
