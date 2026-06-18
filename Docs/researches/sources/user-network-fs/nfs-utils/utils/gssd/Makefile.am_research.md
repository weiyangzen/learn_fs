<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/gssd/Makefile.am

## Purpose
This automake file builds RPCSEC_GSS user-space daemons: `gssd` and, when configured, `svcgssd`. It defines shared GSS/Kerberos context sources and installs binaries under the `rpc.` prefix convention.

## APIs And Build Flow
`COMMON_SRCS` contains context serializers, GSS utilities, OID/name helpers, and error utilities. `gssd_SOURCES` adds `gssd.c`, `gssd_proc.c`, `krb5_util.c`, public headers, and byte-writing helpers. `svcgssd_SOURCES` adds server-side files when `CONFIG_SVCGSS` is enabled. Link flags include support/nfs, libevent, RPCSEC_GSS, Kerberos, GSSAPI, libtirpc, pthread, and optionally nfsidmap for svcgssd. Install hooks rename binaries to `$(RPCPREFIX)$(KPREFIX)<name>` and create `rpc.` manpage symlinks.

## State, Dependencies, And Integration
The file is the build integration point for conditional MIT/Heimdal/lucid Kerberos support, libevent event handling, rpcsec_gss APIs, and package naming conventions.

## Risks And Test Signals
Risks include compile/link matrix complexity across MIT, Heimdal, libtirpc, libgssglue, and service GSS options. Test with `CONFIG_SVCGSS` both ways, Kerberos implementations with and without lucid support, `make install/uninstall DESTDIR=...`, and runtime link checks for libevent/GSSAPI symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/Makefile.am -->
