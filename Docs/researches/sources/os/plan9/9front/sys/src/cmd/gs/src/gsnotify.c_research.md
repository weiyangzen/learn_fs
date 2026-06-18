# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.c

Implements simple notification registration lists.

Key behavior:
- Defines GC descriptors for registrations and notification lists.
- `gs_notify_init` initializes list head and memory allocator.
- `gs_notify_register` allocates a registration node, stores callback/data, and pushes it at the list head.
- `gs_notify_unregister_calling` removes matching registrations by callback and optional data, calls a user-supplied unregister hook per removal, frees nodes, and returns whether anything was found.
- `gs_notify_unregister` is the same without a hook.
- `gs_notify_all` calls all registered callbacks, preserves the first negative error code, and continues notifying remaining callbacks.
- `gs_notify_release` frees all remaining registration nodes.

Dependencies:
- Uses allocator from `gs_notify_list_t`.
- Uses structures declared in `gsnotify.h`.

Research notes:
- Duplicate registrations are allowed.
- Notification iteration stores `next` before invoking callbacks, so callbacks can unregister current entries safely in common cases.
