# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_process.c

## Summary
Implements `ptrace` syscall handling and procfs stop-event support. It performs tracing permission checks, attach/detach, continuation, single-step, process memory I/O, register access, and debugger-induced process stops.

## Main Responsibilities
- Copies ptrace request payloads between userland and kernel temporary storage in `sys_ptrace()`.
- Resolves and validates target processes in `kern_ptrace()`.
- Enforces tracing permissions, jail visibility, setuid restrictions, securelevel restrictions for init, and parent/tracer relationships.
- Implements `PT_TRACE_ME`, `PT_ATTACH`, `PT_DETACH`, `PT_CONTINUE`, `PT_STEP`, `PT_KILL`, memory read/write, `PT_IO`, and register/fpreg/dbreg get/set variants.
- Uses procfs helpers for target memory and register access.
- Provides `stopevent()` for procfs event stops and `trace_req()` as a permissive trace hook.

## Important Behavior
Target processes are held with `PHOLD()` and protected with `p_token`. Tracing is rejected while the target has `P_INEXEC`. Attach reparents the traced process to the tracer and sends `SIGSTOP`; detach attempts to restore the old parent from `p_oppid`, clears tracing flags, and optionally continues with a signal.

Memory access is expressed as `uio` operations against `procfs_domem()`. Register access is similarly routed through procfs architecture helpers. Short or failed integer read/write memory requests are converted to `EINVAL` in some cases.

## Dependencies and Integration
The file depends on process lifetime, LWPs, signals, procfs memory/register routines, architecture ptrace helpers, credentials/caps, and jail checks. It is not filesystem code, but it depends directly on procfs interfaces.

## Risks
Only the first LWP in the process is selected for ptrace operations, marked by the `XXX lwp` comment. Parent restoration during detach can fail if the old parent no longer exists. The procfs memory path returns are normalized in ways that may obscure original `EPERM`/EOF causes.
