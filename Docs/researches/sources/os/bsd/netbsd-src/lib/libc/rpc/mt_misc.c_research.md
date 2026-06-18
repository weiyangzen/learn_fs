# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/mt_misc.c

Read completely: 136 lines.

Defines the global mutexes and rwlocks used across the RPC/libnsl implementation when `_REENTRANT` is enabled. Locks cover service registration, service fd sets, rpcbind address cache, auth caches, raw transports, client fd state, simple-registration lists, socket compatibility creation, and public-key serialization.

Also defines the public/global `rpc_createerr` object and `__rpc_createerr()`. In threaded mode, `__rpc_createerr()` returns a thread-specific `struct rpc_createerr`, lazily allocated via a thread key; in single-threaded mode or allocation failure it falls back to the global object.

This file is infrastructure rather than protocol logic. It is important because many other files assume these lock symbols exist and because `rpc_createerr` has both legacy global and thread-local behavior.
