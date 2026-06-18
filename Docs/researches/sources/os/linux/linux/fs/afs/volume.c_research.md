# File Research: sources/os/linux/linux/fs/afs/volume.c

## Scope

This file manages AFS volume records: VLDB lookup, volume creation/lookup, cell insertion/removal, server-list updates, reference lifetime, fscache activation, and refresh of volume status.

## Public And Internal APIs Covered

- `afs_create_volume()` creates or finds a volume from mount context/VLDB data.
- `afs_try_get_volume()`, `afs_get_volume()`, and `afs_put_volume()` manage references.
- `afs_activate_volume()` and `afs_deactivate_volume()` manage fscache volume cookies.
- `afs_check_volume_status()` refreshes stale or flagged volume records.

## Control Flow And Behavior

- VLDB lookup uses a VL cursor and `VL.GetEntryByNameU`; volume-ID refresh queries pass the ID as a decimal string.
- Volume allocation initializes identity, type, cell ref, name, callback/VolSync fields, locks, mmap list, and server list.
- Insertion into a per-cell RB tree returns an existing live record when possible; otherwise it installs the candidate and links it into proc visibility.
- `afs_create_volume()` applies mount traversal rules: forced type must exist; otherwise RO is preferred if present, then RW.
- Destruction detaches the volume from server lists, removes it from the cell, drops server list and cell refs, traces, and frees via RCU.
- Status update refreshes the volume name and rebuilds the server list. If annotations differ, it swaps in the new list, advances sequence, and reattaches volume/server links.
- Refresh interval is shortened while RO replication is ongoing.
- `afs_check_volume_status()` serializes refreshes with wait/update flags and retries waiters a limited number of times.

## State And Data Structures

- `struct afs_volume` stores VID/type/name, all type VIDs, cell, server-list RCU pointer, update deadline, cache cookie, callback counters, VolSync timestamps, and locks.
- Per-cell volume trees and proc hlist expose active volume records.

## Dependencies

- VL client/rotation, server-list management, fscache, RCU, workqueues, cell locking, and operation keys.

## Risks And Invariants

- Server-list replacement uses RCU and sequence updates with memory ordering.
- Volume records may be reused by concurrent lookups; candidate destruction handles duplicates.
- Refresh waiters return `-ESTALE` after repeated stale/update races.
