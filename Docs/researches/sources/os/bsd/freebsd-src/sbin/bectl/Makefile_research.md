# File Research: sources/os/bsd/freebsd-src/sbin/bectl/Makefile

## Purpose
Builds the ZFS boot environment control utility `bectl`.

## Main Elements
- Includes `src.opts.mk`.
- Sets `PACKAGE=zfs`, `PROG=bectl`, and `MAN=bectl.8`.
- Builds `bectl.c`, `bectl_jail.c`, and `bectl_list.c`.
- Links against `be`, `jail`, `nvpair`, `spl`, `util`, `zfsbootenv`, and `pthread`.
- Adds ZFS/OpenZFS include paths and compatibility defines.
- Enables tests via `HAS_TESTS=yes` and `SUBDIR.${MK_TESTS}+= tests`.

## Dependencies And Integration
Tightly coupled to FreeBSD libbe and in-tree OpenZFS headers/configuration.

## Risk Notes
Build correctness depends on ZFS source tree include paths and generated `zfs_config.h`.
