# File Research: sources/os/plan9/9front/sys/src/9/port/error.h

Declares the kernel’s shared external error string symbols. These include namespace, mount, permission, argument, I/O, networking, process, memory, exec, stat, directory, media, and message-size errors.

The header is widely included by device and kernel subsystems so they can call `error(E...)` using canonical Plan 9 error strings. Definitions live elsewhere; this file is declaration-only.
