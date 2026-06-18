# sources/user-network-fs/nfs-utils/support/nfs/Makefile.am

Purpose: Automake manifest for the internal NFS support libraries.

Important build outputs: builds `libnfs.la` from export parsing, rmtab, RPC, socket, service, qword, string, credential, and file-handle-key helpers. Builds `libnfsconf.la` from `conffile.c` and `xlog.c`. `libnfs.la` links `libnfsconf.la` and `-luuid`.

Control flow: conditional `CONFIG_NFSDCTL` adds `nfsdnl.c`, libnl CFLAGS, nfsdctl include paths, and libnl libraries. `MAINTAINERCLEANFILES` removes generated `Makefile.in`.

State and persistence: no runtime state; controls build graph and link dependencies.

Dependencies and integration: integrates `support/reexport`, optional `utils/nfsdctl`, libuuid, libnl3, and libnl-genl. The `libnfsconf` split allows idmap and plugin components to share configuration/logging without pulling every NFS helper.

Risks: source additions must be represented here or downstream utilities silently miss symbols. Conditional netlink dependencies must match configure results. `libnfs_la_CPPFLAGS` contains reexport include paths that couple support/nfs to reexport internals.

Test signals: run `autoreconf`/Automake generation, build with and without `CONFIG_NFSDCTL`, inspect link lines for libuuid/libnl, and verify installed/private library symbol availability.
