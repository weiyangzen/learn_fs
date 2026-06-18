<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsconf/Makefile.am

## Purpose

This Automake fragment builds and installs the `nfsconf` administrative binary and its man page.

## Important APIs, Types, and Functions

It declares `man8_MANS = nfsconf.man`, `sbin_PROGRAMS = nfsconf`, `nfsconf_SOURCES = nfsconfcli.c`, and links `nfsconf` against `../../support/nfs/libnfsconf.la`.

## Control Flow

Automake turns this into build rules that compile `nfsconfcli.c`, link the support nfs configuration library, install the program into `sbindir`, install the manual page, and clean generated `Makefile.in` during maintainer cleanup.

## State and Persistence Behavior

The file has no runtime state. Its install layout determines where the CLI and documentation persist on target systems.

## Dependencies and Integration Points

It integrates the tool with the top-level nfs-utils build and depends on the local nfs configuration support library that provides `conf_*` APIs used by `nfsconfcli.c`.

## Risks and Edge Cases

Build failures here usually indicate the support library was not configured or generated correctly. Because the binary is installed in `sbindir`, packaging must preserve privileged-admin path expectations.

## Test Signals

Build tests should confirm `make`, `make install DESTDIR=...`, and maintainer cleanup include `nfsconf`, `nfsconf.man`, and the support library dependency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/Makefile.am -->
