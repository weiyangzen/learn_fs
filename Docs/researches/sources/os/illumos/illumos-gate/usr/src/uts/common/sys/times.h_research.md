# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/times.h

## Purpose
Header for process CPU accounting returned by `times(2)`.

## Main Interfaces
- Defines `struct tms` with user, system, children-user, and children-system clock counters.
- Defines `struct tms32` for 32-bit ABI compatibility.
- Declares `clock_t times(struct tms *)`.

## Dependencies And Relationships
Includes `sys/types.h` for `clock_t`. Used by libc/syscall interfaces and process accounting code.

## Research Notes
This is a small, stable POSIX interface; the main compatibility concern is preserving `clock_t` sizing across native and 32-bit ABIs.
