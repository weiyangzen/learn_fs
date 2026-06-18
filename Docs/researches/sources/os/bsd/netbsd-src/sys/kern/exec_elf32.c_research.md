# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_elf32.c

## Purpose
Builds and registers the 32-bit specialization of the shared ELF loader.

## Main Interfaces
- Defines `ELFSIZE 32` and includes `exec_elf.c`, producing 32-bit ELF loader symbols.
- `exec_elf32_execsw[]` registers ELF32 executable switch entries for NetBSD ELF binaries.
- `exec_elf32_modcmd()` adds or removes the ELF32 exec switch on native 32-bit kernels.
- On 64-bit kernels, the module initializes as dormant so ELF32 support symbols remain available for compat layers such as `netbsd32` and `linux32` without registering as a native exec handler.

## Dependencies
Depends on the shared `exec_elf.c` template, `emul_netbsd`, ELF32 aux vector layout, `exec_add()`, `exec_remove()`, `exec_setup_stack()`, and ELF32 core dump support.

## Implementation Notes
`ELF32_AUXSIZE` reserves space for aux entries plus an executable name path. Optional `EXEC_ELF_NOTELESS` support adds a lower-priority generic ELF32 entry when configured.

## Research Notes
This file is a thin registration wrapper; most behavior comes from `exec_elf.c`. Changes here mainly affect whether ELF32 binaries are recognized natively and how much argument-stack space is reserved for auxv data.
