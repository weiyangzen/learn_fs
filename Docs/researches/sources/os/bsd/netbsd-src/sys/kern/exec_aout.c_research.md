# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_aout.c

## Purpose
Implements NetBSD a.out executable format recognition and VM command setup.

## Main Interfaces
- `exec_aout_execsw` registers the executable switch entry for a.out binaries.
- `exec_aout_makecmds()` validates header size, checks native magic values, dispatches to ZMAGIC/NMAGIC/OMAGIC preparation, or calls a CPU hook.
- `exec_aout_prep_zmagic()` maps text/data from the vnode with demand paging and marks text busy.
- `exec_aout_prep_nmagic()` maps text/data with readvn commands and page-aligns data.
- `exec_aout_prep_omagic()` maps combined text/data writable/executable and adjusts data size for `obreak(2)` expectations.
- Module command adds/removes the exec switch entry.

## Dependencies
Uses exec package/vmcmd infrastructure, a.out headers, vnode text marking, UVM VM command helpers, stack setup, and NetBSD native coredump support.
