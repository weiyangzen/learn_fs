# sources/user-network-fs/samba/source4/ntvfs/sysdep/inotify.c

Purpose: `inotify.c` implements the Linux inotify backend for Samba's abstract system change notify layer. It maps SMB change-notify filters onto inotify watches and callbacks.

Important APIs, types, and functions: It defines `inotify_private`, `inotify_watch_context`, `filter_match`, `inotify_dispatch`, `inotify_handler`, `inotify_setup`, `inotify_map`, `watch_destructor`, `inotify_watch`, and `sys_notify_inotify_init`.

Control flow: The first watch lazily initializes an inotify fd and registers it with tevent. `inotify_watch` maps and removes handled bits from the caller's `notify_entry`, adds an `IN_ONLYDIR|IN_MASK_ADD` watch, stores callback state, and returns a talloc handle. When the fd is readable, `inotify_handler` reads all queued events, walks variable-length records, and dispatches actions. Rename cookies are used to emit old/new names, and file renames generate an extra modified event to match SMB expectations.

State and persistence behavior: Runtime state is the inotify fd plus a linked list of watch contexts. Watch removal is controlled by freeing the returned talloc handle; the destructor removes the kernel watch only when no other context uses the same watch descriptor. No durable state is stored.

Dependencies and integration points: It depends on Linux `<sys/inotify.h>`, tevent fd handling, Samba notify NDR types, `sys_notify_register`, and SMB file notify filter constants.

Risks: Inotify coalesces watches, so filtering must be correct per watcher. Not all SMB filters are representable; remaining filter bits are left for generic handling. Event buffer parsing is sensitive to record lengths, and rename pairing is best-effort using adjacent events/cookies.

Test signals: Tests should cover multiple watches on one path, free-handle cleanup, create/delete/rename/attribute events, directory versus file filters, unhandled filter bits, and configure-time gating by `HAVE_LINUX_INOTIFY`.
