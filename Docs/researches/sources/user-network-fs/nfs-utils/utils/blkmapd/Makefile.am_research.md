<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/Makefile.am

## Purpose

This Automake file builds and installs the `blkmapd` pNFS block layout daemon and its manual page.

## Important APIs, Types, and Functions

It declares `man8_MANS = blkmapd.man`, adds `-D_LARGEFILE64_SOURCE` to `AM_CFLAGS`, builds `sbin_PROGRAMS = blkmapd`, compiles device discovery/inquiry/process and device-mapper sources, and links `-ldevmapper` plus `../../support/nfs/libnfs.la`.

## Control Flow

Automake compiles `device-discovery.c`, `device-inq.c`, `device-process.c`, `dm-device.c`, and `device-discovery.h` into the daemon when the parent includes this directory.

## State and Persistence Behavior

The build file has no runtime state. It controls installed daemon and man page artifacts.

## Dependencies and Integration Points

It depends on libdevmapper and nfs-utils support library code. The parent `utils/Makefile.am` includes this directory only under `CONFIG_BLKMAPD`.

## Risks and Edge Cases

Systems without device-mapper development headers/libraries will fail this optional build. Large-file macro consistency matters because the daemon inspects block devices and device-mapper metadata.

## Test Signals

Build with `CONFIG_BLKMAPD` enabled and disabled, verify libdevmapper linkage, install the daemon/man page, and run daemon-level tests against mocked or isolated device discovery where available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/Makefile.am -->
