# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_elf64.c

## Purpose
Builds and registers the 64-bit specialization of the shared ELF loader.

## Main Interfaces
- Defines `ELFSIZE 64` and includes `exec_elf.c`, producing 64-bit ELF loader symbols.
- `exec_elf64_execsw[]` registers native ELF64 execution support.
- `exec_elf64_modcmd()` handles module init/fini by adding or removing the ELF64 exec switch.

## Dependencies
Depends on shared ELF loader code, ELF64 aux vector layout, NetBSD emulation registration, ELF64 core dump generation, and exec switch management.

## Implementation Notes
The primary exec switch entry uses `netbsd_elf64_probe` and first priority. Optional `EXEC_ELF_NOTELESS` support registers a generic ELF64 fallback at `EXECSW_PRIO_ANY`.

## Research Notes
This file is intentionally small and mirrors the 32-bit wrapper without the 64-bit dormant special case. Functional risk is concentrated in registration priority, aux size accounting, and conditional noteless ELF handling.
