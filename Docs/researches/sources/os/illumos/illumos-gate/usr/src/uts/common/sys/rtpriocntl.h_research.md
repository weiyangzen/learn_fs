# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rtpriocntl.h

## Role

`rtpriocntl.h` defines real-time class structures and constants for the `priocntl` system call and scheduler administration.

## Priocntl Structures

`rtparms_t` contains real-time priority and time quantum split into seconds and nanoseconds.

`rtinfo_t` reports the configured maximum real-time priority.

Special values:
- `RT_NOCHANGE`
- `RT_TQINF`
- `RT_TQDEF`

Varargs keys identify RT priority, quantum seconds, quantum nanoseconds, and time-quantum signal.

## Dispatcher Administration

`rtadmin_t` points to an array of `rtdpent` entries and carries entry count and command. `_SYSCALL32` defines `rtadmin32_t`.

Commands:
- `RT_GETDPSIZE`
- `RT_GETDPTBL`
- `RT_SETDPTBL`

## Research Notes

This header is the user/admin ABI for real-time scheduler parameters. Its data layouts must match `rt.h` dispatcher table entries and 32-bit syscall translation.
