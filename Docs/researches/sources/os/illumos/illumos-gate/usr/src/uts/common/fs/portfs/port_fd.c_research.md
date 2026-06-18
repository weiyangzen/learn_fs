# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_fd.c

## Role

Implements `PORT_SOURCE_FD`, the event-port source that monitors file descriptors through the existing `VOP_POLL()`/`pollwakeup()` machinery. It manages per-port fd association caches, pollhead binding, one-shot event delivery, reassociation, dissociation, close cleanup, and fd sharing checks across processes.

## Major Responsibilities

- Associate a file descriptor with a port for poll-style events.
- Reactivate an already associated fd with new event masks and user data.
- Allocate one cached `port_kevent_t` per associated fd.
- Store fd associations in a per-port hash table of `portfd_t`/`polldat_t`.
- Integrate with `addfd_port()`/`delfd_port()` so fd close can clean up port associations.
- Bind `polldat_t` entries to filesystem/device `pollhead_t` values.
- Submit immediate events when `VOP_POLL()` returns readiness.
- Remove queued events during reassociation or dissociation.
- Destroy fd caches during per-process close and last close.

## Key Functions

- `port_associate_fd()` validates the fd, creates the fd source association on first use, allocates cache state, installs the fd into the interested-list, performs `VOP_POLL()`, binds pollheads, and sends immediate events if readiness exists.
- `port_dissociate_fd()` removes the caller-owned fd association, deactivates it by clearing `PORT_KEV_VALID`, removes queued events, and frees the object.
- `port_fd_callback()` enforces cross-process delivery rules and handles close callbacks. For delivery, another process may consume fd events only when it has the same fd number and same `file_t *`.
- `port_cache_lookup_fp()` finds an association by fd number and `file_t`.
- `port_bind_pollhead()` disassociates any prior pollhead, associates the `polldat_t` with the new pollhead, then reruns `VOP_POLL()` to close the race between readiness and pollhead linkage.
- `port_cache_insert_fd()` and `port_cache_grow_hashtbl()` maintain the per-port fd hash table.
- `port_remove_portfd()` removes the fd/port relationship if the fd is still open.
- `port_close_sourcefd()` is the source close callback. It removes all associations owned by the closing pid and, on last close, waits for all outstanding fd entries to disappear before destroying the cache.

## Association Model

Each associated fd owns a cached event slot. The association is active while `PORT_KEV_VALID` is set. When readiness is detected, the code clears `PORT_KEV_VALID`, stores the readiness mask, and sends the cached event. After userspace consumes the event, the application must call `port_associate()` again to reactivate the fd.

Reassociation updates the user pointer and event mask, removes any still-queued old event, clears stale validity, and performs a fresh poll.

## Race Handling

`VOP_POLL()` can drop and reacquire the port fd-cache lock through poll infrastructure. After polling, the code revalidates that the same `portfd_t` still exists and that the registering thread still owns the in-progress association attempt. If another thread dissociated or reassociated the same fd, the function returns the current poll error and leaves application-level synchronization to callers.

`port_bind_pollhead()` reruns `VOP_POLL()` after `polldat_associate()` so a readiness change that occurs between the first poll and pollhead binding is not lost.

## Shareability

Fd events are conditionally shareable after fork or descriptor passing only when the consuming process has the same fd number pointing to the same `file_t`. Dissociation is stricter: only the pid that first associated the fd can dissociate it.

## Research Notes

This file is the bridge between event ports and classic poll. Its key invariant is that a cached fd event is one-shot: valid while armed, invalid once fired, and rearmed only by explicit reassociation.
