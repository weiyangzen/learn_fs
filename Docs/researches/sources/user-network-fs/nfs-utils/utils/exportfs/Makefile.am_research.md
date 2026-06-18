<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/exportfs/Makefile.am

## Purpose
This automake file builds the `exportfs` administration command and packages its related manual pages for exports, nfsd, and exportfs.

## APIs And Build Flow
It declares `man5_MANS = exports.man`, `man7_MANS = nfsd.man`, `man8_MANS = exportfs.man`, and `sbin_PROGRAMS = exportfs`. `exportfs_SOURCES` is `exportfs.c`. Link dependencies include support/export, support/nfs, support/misc, support/reexport, libwrap, libnsl, pthread, and netlink libraries. `exportfs_CPPFLAGS` adds support/reexport and netlink include flags.

## State, Dependencies, And Integration
The file integrates the command with the export database, reexport support, cache flushing, and optional libnl based kernel interfaces. Configure variables provide all portability decisions and library flags.

## Risks And Test Signals
Risks are mostly build-time: optional netlink flags must match compiled code, libwrap/libnsl availability varies by platform, and manpage lists must stay synchronized with distributed files. Test with `make`, `make distcheck`, netlink enabled/disabled builds, and link checks on systems with and without tcp_wrappers/libnsl.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/Makefile.am -->
