# File Research: sources/os/bsd/netbsd-src/sys/sys/clockctl.h

## Scope

Defines `/dev/clockctl` ioctl ABI for privileged time adjustment delegation.

## APIs And Data Structures

- `clockctl_settimeofday` wraps pointers for `settimeofday`.
- `clockctl_adjtime` wraps delta and old-delta pointers.
- `clockctl_clock_settime` wraps clock id and timespec pointer.
- `clockctl_ntp_adjtime` wraps `timex` pointer plus syscall return value.
- Defines ioctls `CLOCKCTL_SETTIMEOFDAY`, `CLOCKCTL_ADJTIME`, `CLOCKCTL_CLOCK_SETTIME`, and `CLOCKCTL_NTP_ADJTIME`.
- Kernel declarations cover attach/open/close/ioctl/init.

## Dependencies

- Includes `sys/ioccom.h`, `sys/time.h`, and `sys/timex.h`.

## Risks And Invariants

- Ioctl structs intentionally contain user pointers; kernel handlers must copy and validate them.
- ABI mirrors time-related system calls.
