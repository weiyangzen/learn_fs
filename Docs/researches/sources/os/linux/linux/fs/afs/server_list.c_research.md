# File Research: sources/os/linux/linux/fs/afs/server_list.c

## Scope

This file builds and maintains per-volume fileserver lists derived from VLDB records and attaches those volume/server relationships to per-server volume lists.

## Public And Internal APIs Covered

- `afs_alloc_server_list()` builds a refcounted `afs_server_list` for a volume.
- `afs_put_serverlist()` releases server uses and frees the list through RCU.
- `afs_annotate_server_list()` compares a replacement list with the existing list.
- `afs_attach_volume_to_servers()`, `afs_reattach_volume_to_servers()`, and `afs_detach_volume_from_servers()` maintain per-server volume linkage.

## Control Flow And Behavior

- Server-list allocation filters VLDB entries by requested volume type.
- RO replication state is inferred from `NEWREPSITE` and usable server counts. If at least half of usable sites are new replicas, old sites are excluded; otherwise new replica sites are excluded.
- `DONTUSE` sites are marked excluded.
- Each VLDB server UUID is resolved to an active `afs_server` record, and duplicate server records are skipped.
- Entries are insertion-sorted by UUID to make replacement comparison and reattachment deterministic.
- Volume attachment inserts each server entry into the server’s volume list in volume-ID order.
- Reattachment preserves callback expiry for unchanged server entries and uses `list_replace()` where possible.

## State And Data Structures

- `struct afs_server_list` holds refcount, lock, number of servers, replication mode, attachment state, sequence, and flexible `servers[]`.
- `struct afs_server_entry` stores server pointer, volume pointer, flags, callback expiry, and list link.

## Dependencies

- VLDB entry parsing, server lookup/creation, per-cell `vs_lock`, and server active-use accounting.

## Risks And Invariants

- Server lists pin active server uses until released.
- Sorted UUID ordering is assumed by comparison and reattachment logic.
- Exclusion flags are annotations that influence rotation but do not remove entries from the list.
