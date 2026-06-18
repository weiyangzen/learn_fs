# File Research: sources/os/plan9/plan9/sys/src/lib9p/intmap.c

This file implements a small locked hash map from `ulong` ids to arbitrary pointers.

Key behavior:
- Uses 128 hash buckets with linked `Intlist` chains.
- `allocmap` stores an optional increment callback used by lookups.
- `lookupkey` read-locks, finds an id, calls the increment callback while locked, and returns the object.
- `insertkey` inserts or replaces an entry, returning the old value without destroying it.
- `caninsertkey` inserts only if absent and returns success/failure.
- `deletekey` removes an entry and returns its value.
- `freemap` walks all buckets, calls an optional destroy callback on each aux pointer, and frees nodes/map.

Important dependencies:
- Used by fid and request pools.
- Relies on callers’ object refcount increment functions being safe under the map lock.

Notable details:
- The source comment explicitly says the map lock protects tree/map structure, not object references; `inc` must provide its own locking discipline.
