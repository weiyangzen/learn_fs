# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.h

Purpose: `sys_lease.h` declares Samba's abstract interface for kernel lease/oplock support.

Important APIs, types, and functions: It declares `sys_lease_send_break_fn`, `struct sys_lease_ops`, `struct sys_lease_context`, and public registration/context/operation functions. The ops table has `init`, `setup`, `update`, and `remove`.

Control flow: The header defines the callback contract: a backend receives opendb entries and can send break notifications through `break_send` using the supplied messaging context. `sys_lease.c` owns selection and dispatch.

State and persistence behavior: `sys_lease_context` holds tevent context, messaging context, break callback, backend private data, and the selected ops table. Backends own any persistent kernel lease state.

Dependencies and integration points: It forward declares opendb, messaging, and tevent types and includes `param/share.h` for share configuration. Backend files include this header to register themselves.

Risks: The `opendb_entry->fd` member is treated by backends as a pointer to an int, so callers must preserve that convention. Missing const protection on some pointers leaves backend misuse possible.

Test signals: Compile tests cover ABI shape; behavioral tests should use a fake backend to verify context creation and setup/update/remove dispatch without Linux-specific fcntl behavior.
