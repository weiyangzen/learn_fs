# File Research: sources/os/linux/linux-stable/fs/ubifs/Makefile

Purpose: Builds UBIFS core and optional feature objects.

Key responsibilities:
- Builds `ubifs.o` under `CONFIG_UBIFS_FS`.
- Includes core journal, file, dir, superblock, tree, scan, replay, log, commit, GC, orphan, budget, LPT, compression, recovery, ioctl, debug, misc, and sysfs objects.
- Adds encryption, xattr, and authentication objects conditionally.

Important interactions:
- Feature object inclusion mirrors Kconfig options for encryption, xattrs, and authentication.

Notable invariants and risks:
- The Makefile shows UBIFS as a single linked object composed of many tightly coupled subsystems.
