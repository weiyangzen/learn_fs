# File Research: sources/os/linux/linux-stable/fs/ecryptfs/Makefile

## Purpose
This Makefile defines the eCryptfs module object composition.

## Build Rules
- `obj-$(CONFIG_ECRYPT_FS) += ecryptfs.o`
- Core objects:
  - `dentry.o`
  - `file.o`
  - `inode.o`
  - `main.o`
  - `super.o`
  - `mmap.o`
  - `read_write.o`
  - `crypto.o`
  - `keystore.o`
  - `kthread.o`
  - `debug.o`
- Messaging-specific objects when `CONFIG_ECRYPT_FS_MESSAGING` is enabled:
  - `messaging.o`
  - `miscdev.o`

## Notes
The file is build metadata only.
