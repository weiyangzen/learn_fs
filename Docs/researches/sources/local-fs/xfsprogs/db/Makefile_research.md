# File Research: sources/local-fs/xfsprogs/db/Makefile

Builds the `xfs_db` libtool command. It derives most `CFILES` from the `HFILES` list and adds standalone command/utility sources such as `bmap_inflate.c`, `btdump.c`, `btheight.c`, `convert.c`, `info.c`, `iunlink.c`, `rdump.c`, and `timelimit.c`. It links against `LIBXFS`, `LIBXLOG`, `LIBFROG`, uuid, realtime, userspace RCU, and pthread libraries, with optional editline/termcap support gated by `ENABLE_EDITLINE`.

Install behavior places `xfs_db` and wrapper scripts `xfs_admin`, `xfs_ncheck`, and `xfs_metadump` under `$(PKG_SBIN_DIR)`. The Makefile is conventional for xfsprogs: it includes shared build definitions/rules, supports dependency generation via `.dep`, and has no local test target.
