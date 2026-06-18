# File Research: sources/os/bsd/openbsd-src/sys/sys/exec.h

This header defines generic exec package state, vmspace construction commands, and legacy machine IDs.

Key definitions:
- User stack process string block: `struct ps_strings`.
- Exec switch: `struct execsw`.
- VM build command: `struct exec_vmcmd`, flags `VMCMD_RELATIVE`, `BASE`, `STACK`, `IMMUTABLE`, `TEXTREL`.
- Command set: `struct exec_vmcmd_set`, `EXEC_DEFAULT_VMCMD_SETSIZE`, `VMCMDSET_INIT`.
- Main exec state: `struct exec_package`, including header, namei/vnode/attrs, vmcmds, text/data/stack layout, flags, interpreter, ELF args, syscall pins, and executable pin region.
- Exec flags: `EXEC_INDIR`, `EXEC_HASFD`, `EXEC_HASARGL`, `EXEC_SKIPARG`, `EXEC_DESTR`, `EXEC_WXNEEDED`, `EXEC_NOBTCFI`, `EXEC_PROFILE`.
- Legacy `MID_*` machine IDs.

Kernel APIs:
- VM command helpers: `vmcmdset_extend`, `kill_vmcmds`, `vmcmd_map_pagedvn`, `vmcmd_map_readvn`, `vmcmd_map_zero`, `vmcmd_mutable`, `vmcmd_randomize`, `new_vmcmd`.
- Exec helpers: `copyargs`, `setregs`, `check_exec`, `exec_setup_stack`, `exec_process_vmcmds`.
- Globals: `execsw[]`, `nexecs`, `exec_maxhdrsz`, `stackgap_random`.

Risk notes:
- `exec_package` coordinates file references, fake script args, interpreter loading, W^X, branch-target CFI, and pinsyscall metadata.
- VM command flags control memory attributes and ASLR-sensitive mapping behavior.
