# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysmsg_impl.h

## Purpose
Defines private `/dev/sysmsg` path and ioctl command constants used by `consadm(8)` to manage auxiliary console devices.

## Main Interfaces
- Device path: `SYSMSG`.
- Ioctls:
  - `CIOCGETCONSOLE`: query auxiliary console device names.
  - `CIOCSETCONSOLE`: set an auxiliary console.
  - `CIOCRMCONSOLE`: remove an auxiliary console.
  - `CIOCTTYCONSOLE`: return the controlling tty `dev_t`.

## Dependencies And Relationships
Used by the sysmsg module and console administration tooling.

## Research Notes
The ioctl semantics are documented in comments, including the two-step size/query behavior for `CIOCGETCONSOLE`.
