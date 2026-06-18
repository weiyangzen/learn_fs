# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_notify.c

Purpose: `sys_notify.c` is the generic registry and selector for system-specific change notify backends.

Important APIs, types, and functions: It exports `sys_notify_context_create`, `sys_notify_watch`, `sys_notify_register`, and `sys_notify_init`. Registered backends are stored in a global array of `struct sys_notify_backend`.

Control flow: Initialization runs static notify backend initializers once. Context creation chooses `notify:backend` from share options or falls back to the first registered backend, checks per-backend `notify:<name>` enable flags, and stores the selected watch callback. `sys_notify_watch` dispatches a watch request or returns `NT_STATUS_INVALID_SYSTEM_SERVICE`.

State and persistence behavior: Backend registration is global process state. Each notify context stores the event context, backend private data, selected backend name, and watch function. Durable filesystem state is not modified.

Dependencies and integration points: It uses Samba module initialization, share option helpers, talloc, tevent, and `sys_notify.h`. The inotify backend registers through this layer.

Risks: If no event context or backend exists, creation returns NULL. Backend selection is simple and can silently create a context with no watch callback if the named backend is disabled or absent. Backends mutate `notify_entry` filter bits to indicate handled parts.

Test signals: Tests should validate backend registration, default selection, explicit backend selection, per-backend disable flags, NULL event context behavior, and watch dispatch/error behavior.
