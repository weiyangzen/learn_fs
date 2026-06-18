# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bplist.c

## Scope

Implements a simple in-memory protected list of block pointers with append and destructive iteration.

Read completely: 77 lines.

## Main APIs

- `bplist_create()` initializes the mutex and list.
- `bplist_destroy()` destroys the list and mutex.
- `bplist_append()` allocates a list entry, copies a `blkptr_t`, and appends it under lock.
- `bplist_iterate()` repeatedly removes the head entry, invokes the caller callback, and frees the entry.

## Control Flow

Iteration removes entries while holding the list lock, drops the lock around the callback, then reacquires it for the next entry. This prevents callback work from blocking producers or other list operations longer than needed.

## State And Dependencies

Uses `bplist_t`, `bplist_entry_t`, illumos `list_t`, mutexes, `kmem_alloc/free`, block pointers, and callback type `bplist_itor_t`.

## Invariants And Risks

- `bplist_iterate()` is destructive: entries are removed and freed after callback invocation.
- The debug variable `bplist_iterate_last_removed` preserves the last removed entry address for callback debugging.
- Callback behavior must tolerate the entry being freed immediately after it returns.
