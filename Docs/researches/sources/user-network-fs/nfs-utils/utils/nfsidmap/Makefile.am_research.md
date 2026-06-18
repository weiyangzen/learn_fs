## sources/user-network-fs/nfs-utils/utils/nfsidmap/Makefile.am

Purpose: Automake rules for building and distributing the `nfsidmap` helper and its man page/config sample.

Important APIs/types/functions: Declares `sbin_PROGRAMS = nfsidmap`, `nfsidmap_SOURCES = nfsidmap.c`, include path for `support/nfsidmap`, and link dependencies on keyutils, `libnfs`, and `libnfsidmap`.

Control flow: Build-system only; automake emits compile/link/install targets.

State and persistence: Installs no runtime state itself. `EXTRA_DIST` ships `id_resolver.conf` and `nfsidmap.man`.

Dependencies and integration: Integrates kernel keyring support through `-lkeyutils` and nfs-utils support libraries.

Risks and test signals: Build failures would show as missing keyutils or support library symbols. Validate with `make nfsidmap`, distribution tarball checks, and install path checks.
