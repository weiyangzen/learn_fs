# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt.h

## Role

Defines public static DTrace probe macros and the lightweight probe descriptor used by SDT instrumentation.

## Key Interfaces

- Userland `DTRACE_PROBE` through `DTRACE_PROBE5` declare and call provider-qualified `__dtrace_<provider>___<name>` functions with `unsigned long` arguments.
- Kernel `DTRACE_PROBE` through `DTRACE_PROBE8` declare and call `__dtrace_probe_<name>` functions with `uintptr_t` arguments.
- Provider convenience macros cover scheduler, process, I/O, iSCSI, NFSv3/v4, SMB/SMB2, IP, TCP, UDP, sysevent, XPV, Fibre Channel, and SRP probe namespaces.
- `SET_ERROR(err)` emits the `set-error` probe and evaluates back to `err`.
- `sdt_probedesc_t` records static probe name, patched instruction offset, and linked-list membership.
- Exports `sdt_prefix`.

## Semantics

Kernel probe macros include explicit type parameters for DTrace type metadata but cast runtime arguments to `uintptr_t`. `SET_ERROR()` evaluates its argument twice, so callers must not pass side-effecting expressions.

## Risk Notes

Probe names are encoded by macro token-pasting and become observable DTrace provider ABI. Renaming or changing arity breaks scripts and provider metadata.
