<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_commondata.c -->
# sources/user-network-fs/libtirpc/src/rpc_commondata.c

Purpose: defines public/global RPC data objects that must have one library-wide storage instance.

Important APIs and state: defines `_null_auth`, `svc_fdset`, `svc_maxfd`, `svc_pollfd`, and `svc_max_pollfd`. These are consumed by service registration, polling, and authentication code.

Control flow: no functions are present. Initialization relies on C static initialization: `_null_auth` is zeroed, `svc_fdset` is zeroed, `svc_maxfd` starts at `-1`, and poll globals start null/zero.

State and persistence: all data is process-global. `svc_fdset`, `svc_maxfd`, `svc_pollfd`, and `svc_max_pollfd` persist for the lifetime of the process or until service code such as `svc_exit()` frees/clears the poll array.

Dependencies and integration points: `svc.c` mutates these globals under `svc_fd_lock`; `svc_run.c` reads `svc_pollfd`; authentication code uses `_null_auth` to initialize reply verifiers. Applications that include legacy RPC globals may also observe `svc_fdset` and `svc_maxfd`.

Risks: process-global mutable service state means multiple independent RPC server subsystems in one process share polling and registration state. Correct locking is external to this file.

Test signals: start and stop multiple transports, verify `svc_fdset`/`svc_pollfd` reflect registrations and unregistrations, call `svc_exit()`, and ensure `_null_auth` remains the zero-flavor verifier used by authentication initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_commondata.c -->
