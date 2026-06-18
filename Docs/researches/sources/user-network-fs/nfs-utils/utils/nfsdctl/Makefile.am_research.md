<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsdctl/Makefile.am

## Purpose

`nfsdctl/Makefile.am` defines the build for the newer `nfsdctl` control utility.

## Important APIs, types, and functions

It builds `nfsdctl` from `nfsdctl.c`, declares `nfsdctl.h`, installs `nfsdctl.8`, applies libnl/libgenl/readline CFLAGS, and links support NFS plus libnl, libgenl, and readline libraries.

## Control flow

Automake expands the declarations into normal build and install rules. There are no custom install hooks in this file.

## State and persistence behavior

The Makefile stores no runtime state. The compiled utility likely controls kernel/server state through netlink and interactive readline support, but those sources are outside this work item.

## Dependencies and integration points

The build dependencies indicate integration with generic netlink and optional interactive command handling. The support NFS library provides shared NFS constants/helpers.

## Risks and edge cases

Link ordering and availability of libnl3, libnl-genl3, and readline determine build success. Distribution must include `nfsdctl.8` and keep `nfsdctl.h` in sync with `nfsdctl.c`.

## Test signals

Build tests should cover library detection flags, successful link, manpage installation, and builds in environments without readline if configure supports disabling it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/Makefile.am -->
