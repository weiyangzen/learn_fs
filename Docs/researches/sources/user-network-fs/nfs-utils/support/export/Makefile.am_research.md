# sources/user-network-fs/nfs-utils/support/export/Makefile.am

Purpose: this Automake file builds the internal `libexport.a` support library and generated mount protocol RPC sources for export-related nfs-utils code.

Important variables and targets: generated files are `mount_clnt.c`, `mount_xdr.c`, and `mount.h` from `mount.x`. `libexport_a_SOURCES` includes client/export/hostname/xtab/cache/auth/v4root/fsloc/v4clients sources plus generated RPC files. CPPFLAGS include `support/reexport` and libnl flags. `RPCGEN` is either the internal built tool or `@RPCGEN_PATH@`. Rules generate client, XDR, and header outputs, and the header rule symlinks `support/include/mount.h`.

Control flow: generated sources are listed in `BUILT_SOURCES`, so they are created before compilation. `dist-hook` removes generated files from distribution snapshots. `CLEANFILES` removes generated outputs and the include symlink.

State and persistence: build-time generated C/header files and a symlink are created. No runtime state.

Dependencies and integration points: depends on rpcgen, libnl cflags, export support sources, and configure's `CONFIG_RPCGEN` conditional. `cache.c` and `auth.c` from this subset are part of this static library.

Risks: parallel builds depend on correct `BUILT_SOURCES` ordering and symlink creation. Generated files must not be shipped in dist archives if `dist-hook` removes them. RPCGEN path mismatches can break bootstrapped builds.

Test signals: run clean parallel builds with internal and system rpcgen; verify generated files exist, the symlink points to `../export/mount.h`, and `make distcheck` succeeds.
