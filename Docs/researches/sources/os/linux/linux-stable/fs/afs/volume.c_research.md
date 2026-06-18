# File Research: sources/os/linux/linux-stable/fs/afs/volume.c

## Scope

Manages AFS volume records, VLDB lookup, volume type selection, fileserver-list replacement, fscache volume activation, and volume-status refresh.

## APIs And Behavior

- `afs_create_volume()` looks up a VLDB entry, applies forced/default RW/RO/backup selection rules, and creates or reuses a cell volume record.
- Allocation initializes volume IDs, name, type, callback/VolSync state, locks, open mmap tracking, and initial server list.
- Volumes are inserted into the cell rb-tree/proc list by volume ID and attached to server volume lists.
- Refcount drop schedules `afs_destroy_volume()`, which detaches from servers, removes cell indexes, drops server list/cell refs, and RCU-frees the record.
- `afs_activate_volume()`/`afs_deactivate_volume()` acquire and relinquish fscache volume cookies when enabled.
- `afs_check_volume_status()` serializes VLDB refreshes, updates renamed volumes and server lists, adjusts refresh interval for RO replication, and handles waiters.

## State And Dependencies

Depends on VL cursor lookup, server-list construction/annotation/reattachment, cell volume locks, fscache, volume flags, and operation keys. Volume server-list replacement uses RCU plus sequence counters.

## Risks And Invariants

Type selection implements AFS mount-point traversal rules. Server-list replacement must preserve attachments and callback expiry where possible. `AFS_VOLUME_WAIT`/`UPDATING` bits serialize refresh and bound stale wait retries.
