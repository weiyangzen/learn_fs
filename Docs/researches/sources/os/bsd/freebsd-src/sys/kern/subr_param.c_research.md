# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_param.c

## Purpose
Initializes global kernel sizing and timing parameters from compile-time defaults, tunables, detected physical memory, and virtualization status.

## Main Interfaces
- `init_param1()`: early boot parameters not scaled by memory.
- `init_param2(long physpages)`: parameters scaled/clamped by physical memory.
- `sysctl_kern_vm_guest()`: stringifies detected VM guest type.

## Implementation Notes
`init_param1()` selects `hz` from `kern.hz`, `HZ`, or `HZ_VM` when running as a guest, clamps it to min/max, then derives `tick`, `tick_sbt`, `tick_bt`, and `tick_seconds_max`. It also initializes stack pages, vnode lock pause max, swap/buffer-cache KVA caps, message buffer size, process size limits, max supplementary groups, PID limit, and unmapped buffer allowance.

`init_param2()` derives `maxusers`, `maxproc`, `maxprocperuid`, `maxfiles`, `maxfilesperproc`, `nbuf`, `bio_transient_maxcnt`, `maxphys`, `nswbuf`, and `maxpipekva`. It clamps process and file limits to memory-derived maxima and rounds `maxphys` up to a power of two when needed.

The VM guest sysctl maps enum values to stable strings and uses a static assert to ensure the table covers all enum values.

## Dependencies
Uses tunables, sysctls, VM page sizing, pmap/kernel address limits, vnode/buffer globals, and scheduler tick globals.

## Research Notes
This file affects filesystem and block I/O through `maxphys`, buffer-cache sizing, vnode timing pause values, message-buffer size, and process/file limits.
