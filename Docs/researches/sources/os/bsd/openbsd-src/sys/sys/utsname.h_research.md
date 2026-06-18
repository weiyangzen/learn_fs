# File Research: sources/os/bsd/openbsd-src/sys/sys/utsname.h

Defines `SYS_NMLN` and the POSIX `struct utsname` fields: system name, node name, release, version, and machine, each 256 bytes.

Outside the kernel it declares `uname(struct utsname *)`. This is stable userland ABI with no filesystem-specific behavior.
