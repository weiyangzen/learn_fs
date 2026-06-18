<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/rpcdebug/Makefile.am

## Purpose

This Automake file builds and installs the `rpcdebug` debug-flag utility and its manual page.

## Important APIs, Types, and Functions

It declares `man8_MANS = rpcdebug.man`, `sbin_PROGRAMS = rpcdebug`, and `rpcdebug_SOURCES = rpcdebug.c`.

## Control Flow

Automake compiles `rpcdebug.c`, installs the binary under `sbindir`, installs the man page, and removes `Makefile.in` during maintainer cleanup.

## State and Persistence Behavior

No runtime state is stored here. Install state consists of the executable and manual page.

## Dependencies and Integration Points

It integrates the proc-sysctl debug flag editor with the nfs-utils build.

## Risks and Edge Cases

The source depends on kernel/user headers exposing NFS debug flag constants; build portability depends on those headers matching the target environment.

## Test Signals

Build tests should compile `rpcdebug` and install its manual page. Runtime tests need a controlled `/proc/sys/sunrpc` environment or mocks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcdebug/Makefile.am -->
