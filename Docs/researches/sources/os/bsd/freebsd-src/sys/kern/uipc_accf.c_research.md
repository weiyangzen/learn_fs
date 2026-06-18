# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_accf.c

## Summary
Implements FreeBSD accept-filter registration and the socket-option plumbing for attaching accept filters to listening sockets. Accept filters can hold newly accepted connections on the incomplete listen queue until a filter callback decides they are ready for `accept(2)`.

## Main Responsibilities
- Maintains the global singly linked list of registered `struct accept_filter` entries.
- Handles generic module load/unload events for accept-filter KLDs.
- Implements `accept_filt_getopt()` and `accept_filt_setopt()` for querying, installing, and removing filters from listen sockets.
- Moves connections blocked solely by a removed accept filter from `sol_incomp` to `sol_comp`.

## Key APIs
- `accept_filt_add()`, `accept_filt_del()`, `accept_filt_get()`.
- `accept_filt_generic_mod_event()`.
- `accept_filt_getopt()`, `accept_filt_setopt()`.

## Important Behavior
`accept_filt_add()` accepts a malloc-owned filter definition. If a name already exists but has a `NULL` callback from a prior unload, the old list entry is reused and the new allocation is freed.

Filter unload is intentionally disabled unless `net.accf.unloadable` is set. Deletion only clears `accf_callback`; the list node is leaked/reused to reduce dangling callback risk after module unload.

Installing a filter requires a listening socket and refuses to replace an existing filter with `EBUSY`. If the filter supplies `accf_create`, that callback runs while the socket mutex is held and must not block.

Removing a filter clears per-socket filter state, calls `accf_destroy` if present, frees the saved filter string, clears `SO_ACCEPTFILTER`, and promotes queued child sockets whose `SO_ACCEPTFILTER` bit kept them incomplete.

## State and Synchronization
The global filter list is protected by `accept_filter_mtx`. Per-socket state uses socket/listen locks. The remove path relies on the listen socket queue invariants while walking and moving sockets between incomplete and complete queues.

## Risks
The unload model is deliberately conservative because callback lifetime is not refcounted. Enabling `net.accf.unloadable` can expose stale callback hazards if sockets still reference unloaded code.
