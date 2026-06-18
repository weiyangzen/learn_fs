<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsd/Makefile.am

## Purpose

`nfsd/Makefile.am` defines the automake build and install rules for the `rpc.nfsd` user-level control program.

## Important APIs, types, and functions

It builds `nfsd` from `nfsd.c` and `nfssvc.c`, installs `nfsd.man`, includes `nfssvc.h` as a non-installed header, and links against the support NFS library plus tirpc. Install hooks rename the binary with `rpc.` and optional kernel prefix and create matching manpage symlinks.

## Control flow

Automake generates normal build targets, then custom install/uninstall hooks rename executables and manage manpage links under `DESTDIR`.

## State and persistence behavior

No runtime state exists in the Makefile. Install rules mutate the target filesystem's sbin and man directories.

## Dependencies and integration points

The build links to `../../support/nfs/libnfs.la`, which provides NFS control macros and library helpers used by `nfsd.c` and `nfssvc.c`.

## Risks and edge cases

As with `mountd`, the install hooks assume automake naming behavior. Manpage symlink targets are derived by replacing `man` suffix with `8`, which depends on local file naming conventions.

## Test signals

Build and packaging tests should cover `make install DESTDIR=...`, uninstall, prefixed binary names, manpage links, and link success with tirpc enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/Makefile.am -->
