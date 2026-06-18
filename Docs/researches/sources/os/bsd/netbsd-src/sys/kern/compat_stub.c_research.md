# File Research: sources/os/bsd/netbsd-src/sys/kern/compat_stub.c

## Purpose
Defines compatibility hook storage and default vectors used by optional or modular compatibility code throughout the kernel.

## Main Interfaces
- NTP vectors point to real NTP functions when `NTP` is built in, otherwise `NULL`.
- SCTP address hooks default to `NULL` and are later patched by network initialization.
- Many global hook structs are defined for USB, ccd, clockctl, crypto, raidframe, puffs, wscons, sysmon, bio, vnd, networking, tty, socket, modstat, proc32, coredump, and other compatibility paths.
- `kern_sig_43_pgid_mask` provides shared state for older signal compatibility.

## Implementation Notes
This file intentionally centralizes hook definitions to avoid link-time circular dependencies between base kernel and optional compat modules/rump components.

## Dependencies
Depends on `sys/compat_stub.h` hook type declarations and optional NTP headers.
