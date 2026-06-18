# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/rwlock.h

## Purpose

`rwlock.h` defines local NDIS-compatible read/write lock structures and constants for CrossNt.

## Main Contents

- Defines `MAXIMUM_PROCESSORS` as 32 if absent.
- Defines `NDIS_RW_LOCK_REFCOUNT`, padding each refcount to a 16-byte cache-line-sized slot.
- Defines `NDIS_RW_LOCK` with a spin lock/context area and per-processor refcounts.
- Defines `LOCK_STATE` containing lock state and old IRQL.
- Defines lock-state constants:
  - free, read acquired, write acquired, recursive, released.
- Defines acquisition mode constants:
  - `RWLOCK_FOR_WRITE`
  - `RWLOCK_FOR_READ`

## Integration Notes

This supports the dynamically resolved NDIS lock routines listed in `CrNtStubs.h`, and provides layout definitions when platform headers do not.

## Risks And Edge Cases

- The NDIS lock layout must match the expected implementation. If NDIS uses a different layout on a target OS, this compatibility definition can break.
- `MAXIMUM_PROCESSORS` fixed at 32 reflects old NT-era assumptions.
