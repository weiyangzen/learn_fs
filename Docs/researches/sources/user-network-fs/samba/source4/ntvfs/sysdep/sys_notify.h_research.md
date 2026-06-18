# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.h

Purpose: `sys_notify.h` declares the abstract interface between Samba change notify code and OS-specific notification backends.

Important APIs, types, and functions: It defines `sys_notify_callback_t`, `notify_watch_t`, `struct sys_notify_context`, `struct sys_notify_backend`, and prototypes for backend registration, context creation, watch setup, and initialization.

Control flow: Backends implement `notify_watch_t`, receive a `notify_entry`, callback, private data, and output handle pointer, then remove handled filter bits from the entry. The callback reports `struct notify_event` back to the higher layer.

State and persistence behavior: `sys_notify_context` stores tevent context, backend private data, name, and selected watch function. Watch handle lifetimes are backend-defined, usually talloc-owned.

Dependencies and integration points: It includes NDR notify types and share configuration declarations. It is consumed by generic notify code and backend modules such as inotify.

Risks: The `void *handle` parameter is really a pointer-to-handle convention, so callers and backends must agree on casting. Mutation of `notify_entry` filters is part of the API and can surprise new backend authors.

Test signals: Fake-backend tests should assert callback signature, handle return behavior, filter-bit mutation, and error propagation through `sys_notify_watch`.
