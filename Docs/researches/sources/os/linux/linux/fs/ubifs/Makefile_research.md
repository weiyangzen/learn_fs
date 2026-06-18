# File Research: sources/os/linux/linux/fs/ubifs/Makefile

Purpose: UBIFS object composition.

Build contents:
- `obj-$(CONFIG_UBIFS_FS) += ubifs.o`
- Core objects include shrinker, journal, file, dir, super, sb, io, tnc, master, scan, replay, log, commit, gc, orphan, budget, find, tnc_commit, compression, lpt/lprops, recovery, ioctl, debug, misc, sysfs.
- Conditional objects: `crypto.o` for `CONFIG_FS_ENCRYPTION`, `xattr.o` for `CONFIG_UBIFS_FS_XATTR`, `auth.o` for `CONFIG_UBIFS_FS_AUTHENTICATION`.

Role:
- Shows `auth.c`, `budget.c`, and `commit.c` are part of the main UBIFS aggregate object, not standalone modules.
