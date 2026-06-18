# sources/user-network-fs/nfs-utils/utils/idmapd/Makefile.am

Purpose: automake definition for building and installing the `idmapd` daemon and its manual page links.

Important build APIs: `sbin_PROGRAMS = idmapd`; sources are `idmapd.c`, `nfs_idmap.h`, and `queue.h`. `AM_CPPFLAGS` includes the support nfsidmap headers. `idmapd_LDADD` links libnfs, libnfsidmap, and libevent.

Control flow: install hooks rename the built binary with `$(RPCPREFIX)$(KPREFIX)` and create prefixed man-page symlinks; uninstall hooks remove those renamed artifacts. The comments document why `program_transform_name` is not used.

State and persistence: affects installed filesystem layout under `$(sbindir)` and `$(man8dir)` rather than runtime state.

Dependencies and integration: ties the daemon to nfs-utils support libraries and libevent. Prefix variables allow distributions to install as `rpc.idmapd` or kernel-prefixed variants.

Risks: custom install hooks can diverge from automake expectations and must match packaging scripts. Test signals include `make install DESTDIR=...`, prefixed binary rename, man symlink creation/removal, and builds with different `RPCPREFIX`/`KPREFIX` values.
