# File Research: sources/virtualization/spdk/lib/util/fd_group.c

This file implements SPDK fd groups on Linux using epoll, plus `-ENOTSUP` stubs for non-Linux builds. An fd group owns event handlers, can be nested under another group, can wrap callback execution, and can expose the current epoll event through thread-local storage.

The Linux implementation stores each registered fd in an `event_handler` with callback, callback argument, fd, epoll event mask, fd type, owner group, name, and a state machine: waiting, running, or removed. Removed handlers are freed immediately unless they are currently in a wait loop, in which case free is deferred until the loop notices `EVENT_HANDLER_STATE_REMOVED`.

`spdk_fd_group_create()` allocates a group and epoll fd. `spdk_fd_group_destroy()` asserts the group has no registered fds, no parent, and no children before closing the epoll fd. `spdk_fd_group_add()`, `spdk_fd_group_add_for_events()`, and `spdk_fd_group_add_ext()` allocate handlers and add them to the root epoll instance. Extended opts use an ABI-size-aware copy pattern for event mask and fd type. `spdk_fd_group_remove()` deletes the fd from the root epoll instance and removes the handler from the owner list.

Nested groups are handled by hoisting child fds into the root epoll fd. `spdk_fd_group_nest()` rejects children that already have parents and parents with wrapper functions, then migrates all child fds from the child epoll fd to the parent root. `spdk_fd_group_unnest()` migrates fds back to the child epoll fd and removes the child link. Migration helpers include recovery paths for partial epoll add/delete failures, returning `-ENOTRECOVERABLE` when state may not be restored.

`spdk_fd_group_wait()` only works on root groups. It calls `epoll_wait()`, marks returned handlers running, optionally drains eventfd counters for `SPDK_FD_TYPE_EVENTFD`, then invokes callbacks directly or through the owner group’s wrapper function. It stores the active epoll event in thread-local `g_event` so `spdk_fd_group_get_epoll_event()` can return it during callback execution.

`spdk_fd_group_event_modify()` updates a registered fd’s event mask with `EPOLL_CTL_MOD`. `spdk_fd_group_set_wrapper()` installs one callback wrapper per group and rejects wrapping groups with children.

Key invariants are root ownership of active epoll registrations, accurate `num_fds` accounting, no blocking wait on nested groups, deferred handler free during callbacks, and no wrapper on a group with nested children.
