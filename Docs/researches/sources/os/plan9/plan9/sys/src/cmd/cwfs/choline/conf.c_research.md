# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/choline/conf.c

Site-specific cwfs configuration for `choline`.

It sets `fs_mktime`, starts filesystem `"main"` at superblock 2, and initializes local parameters including a larger file table (`conf.nfile = 60000`), `firstsb = 12565379`, and smaller large-message count. It enables both `serve9p1` and `serve9p2`.

This build uses the 32-bit, 16 KiB-block layout from its companion `dat.h`.
