# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_ecoff.c

## Purpose
Implements ECOFF executable format recognition and VM command setup.

## Main Interfaces
- `exec_ecoff_execsw` registers the ECOFF executable switch with CPU probe and setregs hooks.
- `exec_ecoff_makecmds()` validates header size/magic, calls the CPU ECOFF probe, dispatches by OMAGIC/NMAGIC/ZMAGIC, and sets up the stack.
- `exec_ecoff_prep_omagic()` maps combined text/data and zeroes BSS.
- `exec_ecoff_prep_nmagic()` maps text and data separately from ECOFF offsets.
- `exec_ecoff_prep_zmagic()` marks text busy and maps text/data demand-paged.
- Module command adds/removes the exec switch entry.

## Dependencies
Uses ECOFF header macros, exec/vmcmd infrastructure, CPU ECOFF hooks, vnode text marking, and NetBSD native coredump support.
