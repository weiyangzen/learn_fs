# File Research: sources/virtualization/libguestfs/lib/Makefile.am

## Role
Autotools build definition for the host-side `libguestfs.la` library and its internal unit test binary.

## Main Contents
- Declares generator-built outputs such as `actions-*.c`, generated headers, POD fragments, symbol file, and struct helpers.
- Builds `libguestfs.la` from common protocol/utils/qemuopts/structs code plus core library modules such as launch, appliance, drives, command, proto, fuse, inspection, copy, create, TSK, YARA, and generated actions.
- Sets include paths for common libraries, gnulib, and public headers.
- Adds external CFLAGS/LIBS for RPC, PCRE2, libvirt, libxml2, SELinux, JSON-C, sockets, clock, gettext, threads, and gnulib.
- Uses version-info tied to `MAX_PROC_NR` and a version script.
- Optionally builds `libvirt-is-version` when libvirt support is enabled.
- Defines `unit-tests` linked against library objects for internal helper testing.
- Generates manpages and HTML from `guestfs.pod` plus generated POD fragments.

## Filesystem/Storage Relevance
This file defines which host-side storage, appliance, protocol, and filesystem helper modules are compiled into libguestfs.
