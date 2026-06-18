# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sdt.c

Read completely: 69 lines.

## Purpose
Provides the base Statically Defined Tracing (SDT) provider symbols and probe trampolines used by DTrace-enabled kernels/modules.

## Main Elements
- Defines the `sdt` provider with `SDT_PROVIDER_DEFINE(sdt)`.
- Exposes `sdt_probe_func`, initially set to `sdt_probe_stub`, for the SDT provider module to replace with the real DTrace probe function.
- Exposes `sdt_probes_enabled` as a frequently-read global flag.
- `sdt_probe_stub()` reports unexpected probe execution and emits a kernel debugger backtrace.
- `sdt_probe()` forwards five explicit arguments plus a zero sixth argument.
- `sdt_probe6()` forwards six probe arguments.

## Dependencies And Integration
Used by SDT probe call sites and loadable DTrace/SDT provider code. Depends on `sys/sdt.h`, kernel printf, and `kdb_backtrace()` for unexpected stub execution.

## Risk Notes
This file is intentionally small. Probe sites rely on `sdt_probes_enabled` and provider setup to avoid calling the stub in unsupported configurations; an unexpected call is treated as diagnostic evidence and backtraced.
