# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/limits.h

## Role

Small illumos system limits header for scatter/gather I/O vector limits.

## Structure

Defines `IOV_MAX` as 1024. Kernel builds also define `IOV_MAX_STACK` as 16, the maximum IOV count intended for on-stack allocation.

## Dependencies And Consumers

No included headers. Consumers are kernel and userland code that need the platform `iovec` count limit; kernel code can use `IOV_MAX_STACK` as an allocation threshold.

## Important Details

This is not the full POSIX `<limits.h>` surface; it is a narrow `sys/limits.h` definition used by illumos components.

## Research Notes

Read completely: 32 lines, 734 bytes.
