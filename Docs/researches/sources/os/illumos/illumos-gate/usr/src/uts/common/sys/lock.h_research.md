# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lock.h

## Role

Legacy process/text/data locking interface constants and prototypes.

## Structure

Defines `UNLOCK`, `PROCLOCK`, `TXTLOCK`, and `DATLOCK`. Kernel builds add `MEMLOCK` and declare `punlock()`. User builds declare `plock(int)`.

## Dependencies And Consumers

No included headers. Userland consumers are legacy `plock(3C)` callers; kernel consumers use internal process/memory unlock support.

## Important Details

`MEMLOCK` is kernel-only. The public ABI surface is intentionally small and inherited from older UNIX behavior.

## Research Notes

Read completely: 60 lines, 1345 bytes.
