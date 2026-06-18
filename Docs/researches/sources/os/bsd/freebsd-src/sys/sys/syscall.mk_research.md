# File Research: sources/os/bsd/freebsd-src/sys/sys/syscall.mk

## Purpose
`syscall.mk` is the generated makefile fragment listing machine-independent syscall stub object files.

## Main Interfaces
- Defines `MIASM` as a backslash-continued list of syscall `.o` files.
- Covers ordinary syscalls, compatibility syscall objects, capability mode calls, VFS/filesystem operations, IPC, networking, threading, jail, audit, POSIX AIO, timerfd, inotify, and recent process-descriptor calls.

## Implementation Notes
The order and names mirror generated syscall definitions. Obsolete or unimplemented syscall numbers do not appear as build objects.

## Dependencies and Constraints
Marked automatically generated and not intended for manual edits. Build correctness depends on consistency with the syscall master source and generated headers.
