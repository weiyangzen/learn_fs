# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease.c

Purpose: `sys_lease.c` provides a generic registry and dispatch layer for kernel lease/oplock backends used by NTVFS.

Important APIs, types, and functions: Public functions are `sys_lease_context_create`, `sys_lease_register`, `sys_lease_init`, `sys_lease_setup`, `sys_lease_update`, and `sys_lease_remove`. It stores registered `struct sys_lease_ops` backends in a global array.

Control flow: Initialization runs statically linked lease backend init functions once. Context creation reads the share option `lease:backend`, matches it case-insensitively against registered backends, stores event/messaging contexts and the break-send callback, and calls the backend `init`. Setup/update/remove simply dispatch through `ctx->ops`.

State and persistence behavior: The registry is process-global and grows as modules register. A lease context is per caller/share and holds only pointers and backend private data. Durable lease semantics are backend/kernel state, not file storage.

Dependencies and integration points: It depends on Samba module initialization, `share_config` option lookup, tevent, messaging, and opendb entries. `sys_lease_linux.c` is the Linux backend when available.

Risks: No backend is selected unless `lease:backend` is explicitly configured; context creation returns NULL otherwise. Dispatch functions assume a valid context and ops table. Duplicate backend registration is not guarded here.

Test signals: Tests should verify module init idempotence, backend selection, missing backend behavior, propagation of backend init failure, and that setup/update/remove calls reach the selected backend.
