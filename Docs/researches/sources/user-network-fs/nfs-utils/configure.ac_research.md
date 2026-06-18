# sources/user-network-fs/nfs-utils/configure.ac

Purpose: `configure.ac` is the Autoconf configuration source for nfs-utils 2.9.1. It defines build options, dependency probes, feature conditionals, generated files, compiler warning policy, and installed path substitutions.

Important options and APIs: options include release, state/config/statd paths, systemd unit installation, NFSv4, blkmapd, GSS/svcgss, kprefix, rpcgen selection, uuid/blkid, mount/libmount, sbin override, junction support, TI-RPC, IPv6, nfsdcld/nfsrahead/nfsdcltrack, nfsdctl, nfsv4server, LDAP/GUMS, and plugin paths. It uses project macros such as `AC_LIBTIRPC`, `AC_LIBCAP`, `AC_LIBXML2`, `AC_TCP_WRAPPERS`, `AC_GETRANDOM`, `AC_LIBEVENT`, `AC_SQLITE3_VERS`, `AC_KEYUTILS`, `AC_KERBEROS_V5`, and `AC_RPCSEC_VERSION`.

Control flow: feature flags are parsed first, then required libraries/headers/functions are probed, then compiler and build-tool state is established. Conditional Automake variables drive subdirectory builds. At the end, path substitutions and warning flags are emitted and a long `AC_CONFIG_FILES` list enumerates generated Makefiles and systemd/pkg-config files.

State and persistence: generated outputs include `support/include/config.h`, Makefiles across the tree, systemd units, and libnfsidmap pkg-config metadata. It exports configured runtime paths such as `NFS_STATEDIR`, `NSM_DEFAULT_STATEDIR`, and `NFS_CONFFILE`.

Dependencies and integration points: this file is the root integration point for libtirpc, libnl3/genl, sqlite, keyutils, Kerberos/GSS, libevent, libblkid, libmount, libxml2, optional LDAP, and kernel netlink headers (`nfsd_netlink.h`, `lockd_netlink.h`, `sunrpc_netlink.h`). It also chooses internal vs system rpcgen.

Risks: it unconditionally defines `HAVE_NFSD_NETLINK` after checking headers, so compatibility fallback headers must be valid when system headers are absent. Many optional features become hard dependency checks when enabled. Strict warning flags can break builds on newer compilers. Cross-compilation paths make assumptions for statd user and sqlite version.

Test signals: configure matrix testing should cover minimal build, NFSv4/GSS enabled and disabled, internal vs system rpcgen, netlink header present/absent, `--disable-uuid`, systemd custom unit dir, junction support, and cross-compilation.
