# File Research: sources/os/bsd/freebsd-src/sys/sys/rtprio.h

Read completely: 94 lines.

## Purpose
Defines realtime/idle/normal priority classes and syscall ABI for `rtprio(2)` and `rtprio_thread(2)`.

## Main Elements
- Maps RTP priority classes to kernel priority classes from `sys/priority.h`.
- Exposes FIFO-related priority macros and helpers.
- Defines realtime priority numeric range, where 0 is highest and 31 is lowest.
- Defines syscall function selectors `RTP_LOOKUP` and `RTP_SET`.
- Defines `struct rtprio` with scheduling class type and priority.
- Kernel side declares conversion helpers between `struct rtprio` and thread priorities.
- Userland side declares `rtprio()` and `rtprio_thread()`.

## Dependencies And Integration
Used by scheduler priority conversion, resource/priority syscalls, userland realtime tools, and POSIX FIFO/RR priority mapping.

## Risk Notes
Class and range semantics must stay aligned with `priority.h` and scheduler implementations; userland ABI depends on `struct rtprio`.
