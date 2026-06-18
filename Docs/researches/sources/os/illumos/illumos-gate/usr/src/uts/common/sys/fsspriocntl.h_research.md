# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fsspriocntl.h

## Role

`fsspriocntl.h` defines Fair Share Scheduler class structures for the `priocntl(2)` system call and `dispadmin(8)` scheduler administration.

## Key Interfaces and Data

- `fssparms_t` carries user priority and user priority limit.
- `fssinfo_t` reports the configured maximum user-priority range.
- `FSS_NOCHANGE` is the sentinel for unchanged priority fields.
- Varargs `priocntl` keys are `FSS_KY_UPRILIM` and `FSS_KY_UPRI`.
- `fssadmin_t` carries scheduler quantum and command for administrative table operations.
- `FSS_GETADMIN` and `FSS_SETADMIN` identify administrative operations.

## Dependencies and Use

The header includes `sys/types.h` and `sys/fss.h`. It is a compact ABI header, visible to userland and kernel consumers.

## Research Notes

This file is purely declarative: no kernel-private state, no inline logic, and no 32-bit alternate structure.
