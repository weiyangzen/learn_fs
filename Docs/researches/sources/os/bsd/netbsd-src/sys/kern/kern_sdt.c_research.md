# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sdt.c

## Purpose

`kern_sdt.c` provides the machine-independent backend glue for Statically Defined Tracing (SDT) kernel probes. It allows code/modules compiled with SDT probes to link and load even when DTrace support is not active.

## Main Responsibilities

- Defines the `sdt` provider with `SDT_PROVIDER_DEFINE(sdt)`.
- Declares SDT link sets:
  - providers;
  - probes;
  - argument types.
- Provides global probe function pointer:
  - `sdt_probe_func`, initially set to `sdt_probe_stub`.
- Defines:
  - `sdt_probe_stub()`
  - `sdt_init()`
  - `sdt_exit()`
- Defines the `sdt:::set-error` probe with one integer argument.

## Behavior

- `sdt_probe_stub()` should not normally be called. If it is called, it prints a diagnostic and dumps known provider/probe/argtype link-set names.
- `sdt_init(void *dtrace_probe)` installs the real DTrace probe function.
- `sdt_exit()` resets the probe function back to the stub.

## Notes

This is a compatibility/linkage layer rather than a full tracing implementation. Actual active probe handling depends on DTrace providing the runtime probe function.
