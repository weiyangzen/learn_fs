# File Research: sources/local-fs/xfsprogs/mkfs/Makefile

This makefile builds and installs the `mkfs.xfs` command and its companion configuration files.

It sets `TOPDIR`, includes common build definitions, declares `LTCOMMAND = mkfs.xfs`, and generates the helper script `xfs_protofile` from `xfs_protofile.py.in` by substituting package version and inlining the gettext initialization snippet. The generated script is made executable.

The compiled sources are `proto.c` and `xfs_mkfs.c`. `CFGFILES` lists mkfs profiles installed into `$(MKFS_CFG_DIR)`: DAX x86_64 and LTS compatibility profiles from 4.19 through 6.18. Link libraries include libxfs, libxcmd, libfrog, librt, libblkid, libuuid, libinih, liburcu, and pthread.

The default target builds dependencies, the command, config files, and protofile. The install target installs the binary to `$(PKG_SBIN_DIR)`, installs the protofile as `xfs_protofile`, creates the mkfs config directory, and installs all config files read-only.
