# File Research: sources/os/bsd/netbsd-src/sys/sys/exec.h

Read completely: 328 lines.

## Purpose
Defines the machine-independent exec framework: process argument metadata, executable-format switch entries, exec packages, VM commands, and exec/posix_spawn kernel entry points.

## Main Interfaces
- User-visible `struct ps_strings` and kernel `struct ps_strings32`.
- `struct execsw`: format handler metadata and callbacks for probing, argument copying, register setup, stack setup, and core dumping.
- `struct exec_package`: pathname/header/vnode/attributes, VM layout, entry point, fake script args, emulation data, interpreter vnode, PaX flags, OS version, machine arch.
- Exec flags: `EXEC_INDIR`, `EXEC_HASFD`, `EXEC_HASARGL`, `EXEC_SKIPARG`, `EXEC_DESTR`, `EXEC_32`, `EXEC_FORCEAUX`, `EXEC_TOPDOWN_VM`, `EXEC_FROM32`.
- `struct exec_vmcmd_set`, `struct exec_vmcmd`, `NEW_VMCMD`, `NEW_VMCMD2`.
- Kernel routines: `exec_makecmds`, `exec_runcmds`, `exec_read`, `check_exec`, `check_veriexec`, `execve1`, `do_posix_spawn`, `exec_add`, `exec_remove`, `exec_sigcode_alloc`, `emul_find_root`, `emul_find_interp`.

## Dependencies And Integration
Connects vnode-backed executable files, namei path resolution, UVM mappings, emulation roots, veriexec, core dump code, and machine-dependent register setup.

## Risks And Edge Cases
- Exec packages carry vnode and interpreter state that must be unwound correctly on failure.
- Fake argument vectors handle script indirection.
- 32-bit emulation uses separate ps-string and ABI flags.
- VM command ordering and flags determine process address-space construction.

## Filesystem Relevance
High. Executables are opened and read through VFS/vnodes; mount `noexec`, vnode permissions, veriexec, and interpreter path lookup all feed exec.
