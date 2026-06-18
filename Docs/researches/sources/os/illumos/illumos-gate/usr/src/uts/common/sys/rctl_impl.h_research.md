# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl_impl.h

## Role

`rctl_impl.h` contains resource-control implementation details shared between userland support code and kernel/user ABI translation.

## Key Definitions

It defines `RCTLCTL_GET` and `RCTLCTL_SET` operation values. Outside the kernel it declares:
- `rctlctl()`
- `rctllist()`
- `setprojrctl()`

`rctl_opaque_t` is the concrete layout behind opaque `rctlblk_t` data. It carries:
- configured and enforced quantities.
- privilege.
- global flag/action and syslog level.
- local flag/action and signal.
- local recipient PID.
- firing time.

The header also declares `rlim_fd_cur` and `rlim_fd_max`.

`RCTLBLK_INC()` advances through an array of `rctlblk_t` objects using `rctlblk_size()` rather than `sizeof`, preserving opacity.

## Research Notes

This header is sensitive because it exposes the internal shape of resource-control blocks while the public API treats them as opaque. Consumers must use `rctlblk_size()`-based stepping for compatibility.
