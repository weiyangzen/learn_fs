# File Research: sources/os/linux/linux-stable/fs/openpromfs/Makefile

## Scope

This Makefile builds the Sun OpenPROM filesystem support.

## Build Behavior

- Adds `openpromfs.o` when `CONFIG_SUN_OPENPROMFS` is enabled.
- Composes `openpromfs.o` from `inode.o`.

## Dependencies And Invariants

- The filesystem implementation is single-source in this directory.
- Build is gated entirely by the architecture/config option for OpenPROMFS support.
