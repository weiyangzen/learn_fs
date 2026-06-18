# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cm.h

## Scope

Complete file read, 65 lines. This is a small common DKTP kernel header for shared includes, opaque typing, and buffer-sector helpers.

## Public Surface

The file includes `sys/types.h` always and several kernel-only headers under `_KERNEL`, including DDI, allocation, open, errno, and device macros. Under `_KERNEL` it defines:

- `opaque_t` as `void *` if SCSI has not already supplied it.
- `PRF` as `prom_printf`.
- `SET_BP_SEC(bp, X)` and `GET_BP_SEC(bp)` for storing/retrieving a sector value via `buf.b_private`.

## Behavior And Integration

The header gives DKTP code a shared way to pass opaque object pointers and to stash sector metadata inside `struct buf`.

## Dependencies And Invariants

`GET_BP_SEC()` casts `b_private` back to `daddr_t`; this assumes the stored sector value safely round-trips through a pointer-sized field. It is only intended for kernel builds.

## Risks

Using `b_private` for sector storage conflicts with any other subsystem using the same buffer field. The pointer/integer cast is architecture-sensitive and should stay confined to legacy DKTP code that already expects this convention.
