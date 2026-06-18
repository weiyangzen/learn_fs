# File Research: sources/local-fs/xfsprogs/repair/Makefile

## Purpose
Builds and installs the `xfs_repair` command and enumerates repair subsystem sources and headers.

## Key Elements
Sets `TOPDIR`, includes build definitions/rules, defines `LTCOMMAND = xfs_repair`, lists repair headers and C files, links against libxfs, libxlog, libxcmd, libfrog, uuid, rt, blkid, urcu, and pthread, and uses `-static-libtool-libs`.

Defines `default: depend $(LTCOMMAND)`, a `globals.o` header dependency, install target for `$(PKG_SBIN_DIR)`, and commented tracing flag names for inode, directory, duplicate extent, btree build, parent pointer, and prefetch debugging.

## Dependencies
Depends on xfsprogs top-level build system variables and `$(BUILDRULES)`.

## Behavior/Risks
The source list makes repair composition explicit; adding repair modules requires updating this file so they are compiled and linked into `xfs_repair`.
