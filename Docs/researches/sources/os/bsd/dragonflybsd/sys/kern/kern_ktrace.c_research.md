# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_ktrace.c

## Purpose

`kern_ktrace.c` implements process-level ktrace support. Unlike KTR's in-memory diagnostic tracepoints, this code writes user-visible trace records for syscalls, returns, path lookups, sysctls, I/O, signals, context switches, and `utrace()` data to a vnode-backed trace file.

## Main Responsibilities

- Builds `struct ktr_header` records with process, LWP, CPU, command, and threaded-state metadata.
- Emits trace payloads for `KTR_SYSCALL`, `KTR_SYSRET`, `KTR_NAMEI`, `KTR_SYSCTL`, `KTR_GENIO`, `KTR_PSIG`, `KTR_CSW`, and `KTR_USER`.
- Implements the `ktrace` syscall for setting, clearing, clearing-by-file, process-group targeting, and descendant targeting.
- Implements `utrace` for user-supplied trace payloads.
- Manages reference-counted `ktrace_node` objects wrapping trace vnodes.
- Enforces trace-control permissions through `ktrcanset()`.

## Trace Record Flow

Trace emitters set `KTRFAC_ACTIVE` to avoid recursive tracing, build a header with `ktrgetheader()`, attach a stack or temporary payload, and call `ktrwrite()`. `ktrwrite()` temporarily references the process trace node, constructs a header-plus-payload `uio`, takes an exclusive vnode lock, stamps the time after locking to avoid trace-file timestamp reversal, and writes with `IO_UNIT | IO_APPEND`. For `KTR_GENIO`, it writes the header and data `uio` as separate append operations.

If a write error occurs, tracing is stopped for all processes using the same trace node, and the kernel logs the failure.

## Control Operations

`sys_ktrace()` opens a regular trace file for set operations, or handles clear operations without one. Positive PIDs target one process; negative PIDs target a process group; `KTRFLAG_DESCEND` walks child processes through `ktrsetchildren()`. `KTROP_CLEARFILE` scans all processes and clears those using the same vnode. Trace-node references are inherited with `ktrinherit()` and dropped with `ktrdestroy()`.

## Security Notes

`ktrcanset()` allows tracing only when the caller is in the same prison and either root or an unprivileged caller whose real IDs match the target's real/saved IDs, the target is not marked root-traced, and the target is not `P_SUGID`. If root sets tracing, `KTRFAC_ROOT` is recorded so only root can later alter it.
