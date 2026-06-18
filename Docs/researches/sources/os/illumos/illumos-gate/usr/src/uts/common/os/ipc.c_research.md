# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ipc.c

## Role

`ipc.c` is the shared System V IPC namespace implementation used by message queues, semaphore arrays, and shared memory segments. It provides common object IDs, key lookup, permission handling, resource-control checks, reference management, removal, enumeration, and zone cleanup.

## Data Model

Each IPC object embeds `kipc_perm_t` as its first member. Objects have owner/creator uid/gid, mode bits, key, project, zone, refcount, list membership, AVL key membership, and an allocated ID.

`ipc_service_t` represents one facility namespace. It owns:
- A power-of-two ID table of `ipc_slot_t`.
- Per-slot sequence numbers and locks.
- An `id_space` allocator.
- An AVL tree for keyed lookup.
- A list of all visible objects.
- Project and zone resource-control handles.
- Facility destructor and RMID callbacks.

IDs combine table index and sequence number, reducing stale-ID reuse hazards.

## Locking Model

The file documents and implements this lock order:

`namespace lock -> slot locks in table order -> p_lock`

ID lookup avoids taking the namespace lock by reading the current table size, taking the computed slot lock, then verifying the table size did not change. Table growth allocates a new table, locks old and corresponding new slots, copies entries, chains the old table from the new one, publishes the new pointer and size, and intentionally keeps old tables reachable because threads may still touch old embedded locks.

## Interfaces

`ipcperm_access()` performs mode, owner/group, supplementary group, zone, and privilege checks. `ipcperm_set/stat` and `ipcperm_set64/stat64` implement common IPC_SET/STAT behavior and auditing.

`ipcs_create()` initializes a namespace; `ipcs_destroy()` tears it down when empty.

`ipc_lookup()` returns a held ID lock for a valid, zone-visible object. `ipc_hold()`, `ipc_rele()`, and `ipc_rele_locked()` manage object references and call the facility destructor when the last removed object reference drops.

`ipc_get()` implements the first phase of GET: keyed lookup or allocation of an invisible object. `ipc_commit_begin()` revalidates key/resource races and prepares project/zone references. `ipc_commit_end()` publishes the object into the table, AVL tree, and used list. `ipc_cleanup()` unwinds failed allocations.

`ipc_rmid()` removes an object after permission checks, calls facility RMID cleanup, and releases the namespace reference. `ipc_ids()` enumerates visible IDs with zone filtering. `ipc_remove_zone()` removes all objects belonging to a zone without holding the service lock across destructors.

## Resource And Zone Handling

Allocation checks both project and zone resource controls before growing or consuming an ID. Object publication increments project and zone usage counters; removal decrements them. Key lookup is keyed by both IPC key and zone ID, so identical keys can exist independently in different zones.

## Research Notes

This file is concurrency-heavy infrastructure. Audit-sensitive areas are lock ordering during table growth, stale-table lock validation, `ipc_get()`/`ipc_commit_begin()` races, resource-control accounting rollback, zone visibility rules, and deferred destruction after RMID.
