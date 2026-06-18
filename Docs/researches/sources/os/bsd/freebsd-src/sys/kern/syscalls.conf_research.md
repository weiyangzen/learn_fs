# File Research: sources/os/bsd/freebsd-src/sys/kern/syscalls.conf

## Purpose
Small generation configuration file for FreeBSD syscall artifacts.

## Main Elements
- `libsysmap="../../lib/libsys/syscalls.map"`: output or companion path for libsys syscall map generation.
- `libsys_h="../../lib/libsys/_libsys.h"`: output or companion path for generated internal libsys header data.
- `sysmk="../sys/syscall.mk"`: output or companion path for generated syscall makefile fragments.
- `syshdr_extra="#define \tSYS_exit\tSYS__exit"`: extra syscall header define mapping `SYS_exit` to `SYS__exit`.

## Dependencies And Integration
Used by the syscall generation tooling that emits kernel syscall tables, syscall names, headers, makefile fragments, and libsys metadata. It links the kernel syscall source definitions to generated artifacts under `sys/` and `lib/libsys/`.

## Risk Notes
Although only four lines, path or macro changes affect generated syscall ABI support files. The `SYS_exit` alias preserves expected user/kernel naming compatibility and should remain synchronized with generated syscall headers.
