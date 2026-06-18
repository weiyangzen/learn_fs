# File Research: sources/os/bsd/netbsd-src/sys/kern/init_sysctl_base.c

## Purpose
Creates base sysctl tree nodes and minimal `kern`/`hw` nodes shared by normal kernels and rump kernels.

## Main Interfaces
- `sysctl_basenode_init()` creates permanent top-level nodes: `kern`, `vm`, `vfs`, `net`, `debug`, `hw`, `machdep`, `user`, `ddb`, `proc`, `vendor`, `emul`, and `security`.
- `SYSCTL_SETUP(sysctl_kernbase_setup)` registers base kernel identity nodes such as `ostype`, `osrelease`, `osrevision`, `version`, `hostname`, `domainname`, and `rawpartition`.
- `SYSCTL_SETUP(sysctl_hwbase_setup)` registers hardware identity/capability nodes such as `model`, `machine`, `machine_arch`, `ncpu`, `byteorder`, `physmem`, `pagesize`, `alignbytes`, `physmem64`, and `ncpuonline`.
- `sysctl_hw_machine_arch()` returns per-process machine architecture where applicable.
- `sysctl_setlen()` updates cached hostname/domainname lengths after writes.

## Dependencies
Uses sysctl infrastructure, kernel identity globals, CPU model hooks, memory sizing globals, disklabel constants, and process machine-architecture selection macros.

## Implementation Notes
This file intentionally contains a smaller base set than `init_sysctl.c` because rump kernels cannot use the full kernel sysctl initializer.

## Research Notes
This is foundational sysctl setup. Changes here affect early sysctl tree shape and compatibility for both full NetBSD kernels and rump kernels.
