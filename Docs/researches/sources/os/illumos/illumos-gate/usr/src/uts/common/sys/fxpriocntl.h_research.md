# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fxpriocntl.h

## Role

`fxpriocntl.h` defines the fixed-priority scheduling class ABI for `priocntl(2)` and `dispadmin(8)`.

## Key Interfaces and Data

- `fxparms_t` carries fixed-priority user priority, user priority limit, and time quantum seconds/nanoseconds.
- `fxinfo_t` reports the maximum configured user priority.
- Sentinels: `FX_NOCHANGE`, `FX_TQINF` for infinite quantum, and `FX_TQDEF` for default quantum.
- Varargs keys: `FX_KY_UPRILIM`, `FX_KY_UPRI`, `FX_KY_TQSECS`, and `FX_KY_TQNSECS`.
- `fxadmin_t` points at `fxdpent` entries and carries count/command.
- `_SYSCALL32` defines `fxadmin32_t` for ILP32 callers.
- Administrative commands are `FX_GETDPSIZE`, `FX_GETDPTBL`, and `FX_SETDPTBL`.

## Dependencies and Use

This header includes `sys/types.h` and `sys/thread.h` for priority and `fxdpent` dependencies. It is an ABI companion to kernel state in `fx.h`.

## Research Notes

The admin structure embeds a pointer, so 32-bit compatibility is explicit and important.
