## sources/user-network-fs/libtirpc/src/mt_misc.c

Purpose: Centralizes libtirpc global synchronization primitives, thread-specific-data keys, and thread-safe access to `rpc_createerr`.

Important APIs and control flow: The file initializes many mutexes/rwlocks used across service lists, fd sets, auth caches, client fd locks, raw transports, netconfig, port binding, and ops initialization. It declares TSD keys for broadcast, `rpc_call`, TCP/UDP, netconfig errors, rpc create errors, netgroups, and key calls. `__rpc_createerr` lazily creates the `rce_key`, allocates a per-thread `struct rpc_createerr`, installs it, and falls back to the global `rpc_createerr` on allocation/key failure. `tsd_key_delete` deletes initialized pthread keys.

State and persistence: This file is almost entirely process-global state. Per-thread create-error storage persists until key destructor/free.

Dependencies and integration: Every major transport/auth/service module relies on these locks by extern declaration.

Risks and test signals: `tsd_key_delete` appears to delete `rce_key` when checking `rg_key`, likely a typo. Tests should cover per-thread `rpc_createerr` isolation, lock symbol linkage, repeated key creation, and cleanup behavior under sanitizers.
