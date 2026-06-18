# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_ktrace.c

## Purpose
Implements kernel tracing (`ktrace`) state management, trace record construction, permission checks, trace syscall control, and append writes to trace vnodes.

## Main Responsibilities
- Sets and clears per-process trace state with `ktrsettrace()` and `ktrcleartrace()`.
- Initializes trace headers with pid/tid/command metadata.
- Emits trace records for syscall entry/return, namei, genio, signals, structs, user records, exec args/env, pledge failures, and pinsyscall events.
- Implements `sys_ktrace()` and `doktrace()` to enable/disable tracing for pid, process group, or descendants.
- Recursively applies operations with `ktrsetchildren()`.
- Writes records with `ktrwrite()`, `ktrwrite2()`, and `ktrwriteraw()`.
- Enforces trace permission policy with `ktrcanset()`.

## Key Data
- Per-process `ps_traceflag`, `ps_tracevp`, and `ps_tracecred`.
- `KTRFAC_ROOT` marks tracing established by root and restricts later modification.
- Trace records are written as `struct ktr_header` plus up to two payload iovecs.

## Notable Behavior
- Trace vnode references and credentials are held while active; vnode `v_writecount` is adjusted.
- `ktrwriteraw()` appends with `IO_UNIT | IO_APPEND`.
- Any write failure logs a notice and clears tracing for all processes using that vnode/credential pair plus the current process.
- Trace construction sets `P_INKTR` to avoid tracing recursion.

## Security
`ktrcanset()` allows tracing only when caller real uid/gid match target real/saved ids, target is not sugid/root-traced, or caller is root.

## Dependencies
Uses VFS/namei, credentials, process lists, syscalls, pledge/unveil for opening trace files, scheduler pause for large trace writes, ktrace points from other kernel files, and kernel lock for vnode writes.

## Research Notes
The trace output path is intentionally conservative: failures disable tracing broadly for the affected output.
