## sources/user-network-fs/nfs-utils/utils/nfsstat/Makefile.am

Purpose: Automake rules for building `nfsstat`, the NFS statistics reporting utility.

Important APIs/types/functions: Declares `nfsstat.c` as the only source, applies libnl CFLAGS, and links export, nfs, misc, libnl3, and libnl-genl libraries.

Control flow: Build-only. Automake emits compile, link, install, distribution, and maintainer cleanup rules.

State and persistence: No runtime state; ships `nfsstat.man`.

Dependencies and integration: The libnl dependencies match `nfsstat.c` server-stat netlink support, while support libraries cover shared nfs-utils helpers.

Risks and test signals: Missing libnl causes build failure; packaging tests should verify the man page and program are installed together.
