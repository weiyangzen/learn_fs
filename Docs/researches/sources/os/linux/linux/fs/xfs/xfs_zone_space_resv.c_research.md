# File Research: sources/os/linux/linux/fs/xfs/xfs_zone_space_resv.c

## Purpose

Implements zoned XFS space reservation accounting. It reserves both user-visible realtime extents and immediately available write space, coordinating waiters with GC.

## Main Responsibilities

- Calculates default reserved blocks for realtime extents and immediately available blocks.
- Maintains per-task reservation waiters.
- Wakes reservation waiters on shutdown or new available space.
- Adds newly available blocks and wakes waiters in reservation order.
- Reserves immediately available blocks, waiting for GC when needed.
- Implements greedy partial reservation for short writes.
- Reserves and unreserves zoned allocation contexts.

## Important Invariants

- Zoned allocator treats realtime extents and filesystem blocks interchangeably because `rextsize > 1` is unsupported.
- `XC_FREE_RTEXTENTS` is user capacity; `XC_FREE_RTAVAILABLE` is instantly writable capacity.
- Waiters are queued under `zi_reservation_lock`.
- Reserved-pool callers bypass the waiter list.
- NOWAIT callers return `-EAGAIN` instead of sleeping.
- Failed available-space reservation returns the user-visible extent reservation.

## Dependencies

Uses XFS free counters, inodegc flushing, zoned GC state, reclaimable checks, reservation waitqueues, and open-zone ref release.

## Research Notes

This file bridges logical filesystem ENOSPC behavior and the physical constraint that zoned filesystems may need GC before free space is immediately writable.
