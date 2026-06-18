# File Research: sources/os/bsd/freebsd-src/sys/sys/procctl.h

Read completely: 169 lines.

## Purpose
Defines the user/kernel command ABI for `procctl(2)`, including process protection, reaper control, tracing/coredump controls, capability-trap behavior, ASLR/protection policy, no-new-privs, W^X, and signal-exit logging.

## Main Elements
- Reserves machine-dependent command space starting at `PROC_PROCCTL_MD_MIN` and includes `<machine/procctl.h>`.
- Defines command numbers `PROC_SPROTECT` through `PROC_LOGSIGEXIT_STATUS`.
- Defines protected-process operations and inheritance/descendant flags.
- Defines reaper status, descendant PID query, and reaper kill structures with fixed padding for ABI stability.
- Defines reaper, trace, trapcap, ASLR, PROT_MAX, stack-gap, no-new-privs, W^X, and logsigexit control/status constants.
- Declares `procctl(idtype_t, id_t, int, void *)` for userland.

## Dependencies And Integration
Used by `kern_procctl.c`, process reaper state in `struct proc`, security policy toggles in `p_flag2`, machine-dependent procctl extensions, and userland tools controlling process subtrees and hardening policy.

## Risk Notes
Command numbers and structure layouts are syscall ABI. Padding fields preserve forward compatibility; changing constants or layout would affect existing binaries and process-management tools.
