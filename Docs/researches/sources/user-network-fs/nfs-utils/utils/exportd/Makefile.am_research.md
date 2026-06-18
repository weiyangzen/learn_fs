<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/exportd/Makefile.am

## Purpose
This automake file builds and installs the NFSv4 `exportd` daemon and its man page. It wires the program to nfs-utils support libraries and preserves the project convention of installing daemons with an `nfsv4.` prefix plus optional kernel prefix.

## APIs And Build Flow
`sbin_PROGRAMS = exportd` with `exportd_SOURCES = exportd.c`. Link inputs include `libexport.a`, `libnfs.la`, `libmisc.a`, `libreexport.a`, optional junction support, blkid, pthread, uuid, and netlink libraries. `exportd_CPPFLAGS` adds the support/export include path. Hook targets rename the installed binary to `$(NFSPREFIX)$(KPREFIX)exportd` and create/remove `nfsv4.` manpage symlinks.

## State, Dependencies, And Integration
The build depends on configure variables such as `CONFIG_JUNCTION`, `LIBNL3_LIBS`, `LIBNLGENL3_LIBS`, `LIBPTHREAD`, `LIBBLKID`, and `KPREFIX`. It integrates exportd with shared export/cache/nfs support code and packaging install conventions.

## Risks And Test Signals
Risks include manual install hooks diverging from automake transform behavior, missing netlink or uuid libraries surfacing only at link time, and manpage symlink assumptions. Test signals are `make`, `make install DESTDIR=...`, `make uninstall DESTDIR=...`, builds with and without `CONFIG_JUNCTION`, and validation that `nfsv4.exportd` and man links are installed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/Makefile.am -->
