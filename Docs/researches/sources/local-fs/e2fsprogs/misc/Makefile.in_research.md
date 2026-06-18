# File Research: sources/local-fs/e2fsprogs/misc/Makefile.in

## Purpose
Autoconf makefile template for building, profiling, statically linking, installing, uninstalling, cleaning, and dependency-tracking the `misc` e2fsprogs tools.

## Build Contents
Defines programs including:
- System/root tools: `mke2fs`, `badblocks`, `tune2fs`, `dumpe2fs`, `blkid`, `logsave`, `e2image`, `fsck`, `e2undo`.
- User tools: `chattr`, `lsattr`, `uuidgen`, `filefrag`, `e2freefrag`, optional `uuidd`, `e4defrag`, `e4crypt`, `fuse2fs`.
- Test/helper/fuzz targets: `base_device`, `check_fuzzer`, `e2fuzz`, `tst_ismounted`.

## Rules
- Builds normal, profiled, and selected static variants.
- Generates `mke2fs.conf` and `default_profile.c`.
- Builds shared journal/recovery/revoke objects from `debugfs` and `e2fsck` sources with special include flags.
- Generates manpages from `.in` templates via substitution.

## Install Behavior
- Installs root/sbin, sbin, bin, libdir helpers, man1/man5/man8 pages.
- Creates compatibility links such as `mkfs.ext2/3/4`, `e2label`, `e2mmpstatus`, and optionally `findfs`.
- Installs or updates `mke2fs.conf`, preserving old/custom configurations when needed.

## Risks / Notes
- Dependency lines are generated and form the trailing section.
- Optional program inclusion is controlled by configure substitutions such as `@BLKID_CMT@`, `@FUSE_CMT@`, `@UUIDD_CMT@`, and Linux-specific comments.
