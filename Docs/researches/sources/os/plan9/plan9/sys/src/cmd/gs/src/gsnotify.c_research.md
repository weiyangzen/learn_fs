# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.c

Implements a simple notification-list mechanism. `gs_notify_init` stores allocator and empty head. `gs_notify_register` allocates a registration node and prepends it. `gs_notify_unregister_calling` removes matching registrations, optionally all entries for a procedure when `proc_data` is null, invokes a caller-provided unregistration callback, and frees nodes. `gs_notify_unregister` uses a no-op callback.

`gs_notify_all` walks the list while caching `next` before callback invocation, calls every client even if errors occur, and returns the first negative error. `gs_notify_release` frees all registrations.

GC descriptors are defined for registration nodes and lists, so notification lists can be embedded in GC-managed structures.
