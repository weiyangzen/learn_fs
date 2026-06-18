# File Research: sources/os/linux/linux-stable/fs/adfs/dir_fplus.h
- Purpose: Defines on-disk structures and constants for ADFS F+ directories.
- Main structures: `adfs_bigdirheader`, `adfs_bigdirentry`, and `adfs_bigdirtail`.
- Constants: Defines maximum F+ name length and header/tail magic values.
- Integration: Used by `dir_fplus.c` and included by mount/super code for root directory sizing decisions.
- Research notes: This file captures the large-directory disk format contract.
