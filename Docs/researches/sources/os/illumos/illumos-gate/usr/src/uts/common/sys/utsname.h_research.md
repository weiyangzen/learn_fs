# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utsname.h

## Role

Defines the `uname(2)` system identity structure and namespace-dependent declarations.

## Key Interfaces

- Defines `_SYS_NMLN` as 257 and conditionally exposes `SYS_NMLN`.
- `struct utsname` contains `sysname`, `nodename`, `release`, `version`, and `machine` arrays.
- Conditionally exposes global `utsname` under non-strict/extension namespaces.
- Userland declares `uname()`, with special i386 compatibility handling for old SVID behavior through `_nuname`.
- Kernel declares `uts_nodename()` to retrieve the nodename as seen by the current process zone.

## Risk Notes

`struct utsname` element size is ABI-visible and must support Internet hostnames. i386 symbol remapping preserves historical behavior and should not be disturbed casually.
