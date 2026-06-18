# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_slrc.c

## Purpose

`nfs4x_slrc.c` implements a slot-table abstraction used by NFSv4.1 session/backchannel replay-cache support. It provides allocation, lookup, resize, free, state transitions, cleanup callbacks, and callback-busy checks for `slot_ent_t` objects stored in an AVL tree.

## Main Interfaces

Low-level slot-table functions:

- `sltab_create`, `sltab_destroy`, `sltab_resize`, `sltab_query`, `sltab_set_cleanup`
- `sltab_get`, `slot_alloc`, `slot_delete`, `slot_free`
- `slot_incr_seq`, `slot_cb_status`, `slot_set_state`, `slot_error_to_inuse`

Wrapper names:

- `slot_table_create`, `slot_table_destroy`, `slot_table_resize`, `slot_table_query`, `slot_get`

## Data Structures And Locking

The table token `stok_t` owns:

- An AVL tree of `slot_ent_t` records keyed by slot number.
- Current width (`st_currw`) and free-slot count (`st_fslots`).
- A table mutex and condition variable.
- An optional cleanup callback invoked as slots are deleted.

Each `slot_ent_t` has its own mutex and condition variable, slot number, sequence id, state bits, and client-associated fields.

The intended locking order is table lock first, then slot lock. Creation initializes locks and the AVL tree. Destruction walks the tree and deletes every slot under the table lock.

## Allocation And Resize Behavior

`slot_alloc()` searches slot numbers from zero up to current width. If no node exists for a slot, it creates one with sequence id 1 and `SLOT_INUSE`. If a node exists and is marked `SLOT_FREE`, it transitions it to `SLOT_INUSE`.

With `SLT_NOSLEEP`, allocation fails immediately when no slot is available. With `SLT_SLEEP`, it waits on `st_wait` until `st_fslots` indicates availability, then retries the scan.

`sltab_resize()` supports increasing width by adding to `st_fslots`. When decreasing width, it deletes nodes whose slot numbers exceed the new maximum. Consumers retain only the opaque token and do not see the underlying AVL storage change.

## State And Callback Handling

`slot_free()` marks a slot free, increments the free count, signals waiters, and preserves the slot object for reuse. `slot_incr_seq()` atomically increments the per-slot sequence id.

`slot_cb_status()` is used when destroying sessions with backchannel slots. If any slot is still `SLOT_INUSE`, it returns `NFS4ERR_BACK_CHAN_BUSY`. Otherwise it marks slots free and updates the free count.

`slot_set_state()` ORs new state bits into a slot. `slot_error_to_inuse()` clears `SLOT_ERROR` while requiring both `SLOT_ERROR` and `SLOT_INUSE`.

## Dependencies

This file depends on illumos AVL, mutex, condition-variable, and atomic primitives, plus NFSv4.1 slot types from NFS headers.

## Research Notes

The file is generic slot infrastructure rather than protocol execution. Audit-sensitive areas are free-slot accounting during resize/delete/free, lock ordering around AVL lookup and slot mutation, and callback-busy detection before session teardown.
