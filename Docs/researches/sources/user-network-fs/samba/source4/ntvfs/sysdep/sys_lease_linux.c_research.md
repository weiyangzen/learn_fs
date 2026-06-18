# sources/user-network-fs/samba/source4/ntvfs/sysdep/sys_lease_linux.c

Purpose: `sys_lease_linux.c` implements the lease backend using Linux `fcntl(F_SETLEASE)` and realtime signal delivery to support Samba oplock breaks.

Important APIs, types, and functions: It defines `linux_lease_pending`, global `leases`, `linux_lease_signal_handler`, `linux_lease_pending_destructor`, `linux_lease_init`, `linux_lease_setup`, `linux_lease_update`, `linux_lease_remove`, `linux_lease_ops`, and `sys_lease_linux_init`.

Control flow: Backend init registers a tevent signal handler for `SIGRTMIN+1`. Setup ignores no oplocks, downgrades level-II oplocks to none because Linux leases do not support them, allocates a pending lease record for exclusive oplocks, sets the fd's signal with `F_SETSIG`, then sets a write lease with `F_SETLEASE`. On signal, the handler finds the pending entry by `si_fd` and calls `break_send(..., OPLOCK_BREAK_TO_NONE)`. Update/remove free the pending record, whose destructor unlocks the lease.

State and persistence behavior: Pending lease records are kept in a process-global linked list. Kernel lease state is tied to the fd and removed when the pending talloc object is freed or fd is invalid. No disk persistence is involved.

Dependencies and integration points: It depends on Linux fcntl lease support, tevent signal handling, opendb entries, cluster server IDs, and the generic `sys_lease` registry.

Risks: Global state plus signal-driven callbacks make lifecycle ordering important. The code compares `opendb_entry.fd` pointer identity in update/remove but compares actual fd value in the signal handler. Level-II oplocks are silently denied. Signal availability and `SA_SIGINFO` configure checks are platform-sensitive.

Test signals: Tests should cover setup failure paths for invalid fds, signal-triggered break callback with a real leased fd, cleanup on remove/update, level-II downgrade, and configure gating on `HAVE_F_SETLEASE_DECL`.
