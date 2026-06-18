# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types32.h

## Purpose
Fixed-width 32-bit ABI companion types for use by 64-bit kernels and compatibility code.

## Main Interfaces
- Defines 32-bit address, disk, offset, inode, block count, ID, device, key, mode, UID/GID, link count, PID, size, time, clock, and pointer integer aliases.
- Defines `struct timeval32`, `timespec32_t`, `timestruc32_t`, and `struct itimerspec32`.

## Dependencies And Relationships
Includes `sys/int_types.h`. Used by 64-bit kernel code translating ILP32 system call arguments and structures.

## Research Notes
This header is strictly layout-oriented; its definitions should remain fixed-width and independent of native compilation model.
