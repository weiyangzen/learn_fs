# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/portfs/port_vnops.c

## Role

Defines vnode operations for event-port vnodes. These vnodes are not normal filesystem files; they represent kernel event queues exposed as file descriptors.

## Major Responsibilities

- Provides the `port_vnodeops_template` used by `port.c`.
- Implements open, close, getattr, access, inactive, realvp, and poll behavior for `VPORT` nodes.
- Coordinates per-process close cleanup versus final port destruction.
- Discards non-shareable or owner-specific events when a process closes a shared port descriptor.
- Wakes pollers based on queued events and available queue capacity.
- Frees port resources on vnode inactive.

## Key Functions

- `port_open()` is a no-op for already-created port vnodes.
- `port_close()` performs the critical close lifecycle:
  - For non-last close, clears alert mode owned by the current pid, calls source close callbacks for that pid, and discards owned non-shareable events.
  - For last close, marks `PORTQ_CLOSE`, wakes/waits for active getters, calls source close callbacks with `lastclose`, waits for outstanding events, destroys fd cache if unused, and calls `port_close_events()`.
- `port_discard_events()` marks current-process non-shareable events as `PORT_KEV_FREE`.
- `port_close_events()` drains queued events, invokes close callbacks, frees event records, and waits for pending `pollwakeup()` interactions.
- `port_poll()` reports `POLLIN` when queued events exist and `POLLOUT` when the queue has remaining capacity; it also installs the port pollhead for future wakeups.
- `port_getattr()` synthesizes attributes for the event-port vnode.
- `port_inactive()` decrements global counters, frees the vnode, destroys locks, and frees `port_t`.
- `port_access()` allows access unconditionally.
- `port_realvp()` returns the port vnode itself.

## Close Semantics

Event ports can be shared across processes through fork or fd passing. A non-last close removes only resources owned by the closing process. Last close requires full teardown and waits until all event slots allocated to sources have either been queued back to the port or freed.

## Poll Semantics

The port vnode behaves as readable when events are queued and writable when more event slots may be allocated. Poll waiters use `pp->port_pollhd`, and flags in `portq_flags` remember whether `POLLIN` or `POLLOUT` wakeups are needed.

## Research Notes

This file owns the vnode-facing lifetime rules. It is small, but it is where shared-port semantics and final cleanup become observable through standard file descriptor operations.
