# sources/user-network-fs/libnfs/lib/init.c

## Purpose
Core libnfs RPC context initialization, configuration, error handling, cleanup, PDU/fragment cancellation, service registration, and iovec cursor utilities.

## Important APIs, Types, And Functions
- Time helpers: `rpc_current_time`, `rpc_current_time_us`.
- Context lifecycle: `rpc_init_context`, `rpc_init_server_context`, `rpc_init_udp_context`, `rpc_destroy_context`.
- Configuration: `rpc_set_hash_size`, `rpc_set_interface`, `rpc_set_debug`, `rpc_set_username`, `rpc_set_auth`, `rpc_set_uid`, `rpc_set_gid`, `rpc_set_auxiliary_gids`, mountport/poll/timeout setters/getters.
- Error/stat APIs: `rpc_set_error`, `rpc_set_error_locked`, `rpc_get_error`, `rpc_get_stats`.
- Cleanup: `rpc_error_all_pdus`, `rpc_purge_all_pdus`, `rpc_free_all_fragments`.
- Vector helpers: `rpc_add_iovector`, cursor advance/shrink/memcpy/reset/free.

## Control Flow
Client initialization allocates a context, creates hash queues, initializes locks, creates default AUTH_UNIX auth, seeds XID with time/pid/salt, sets fd and uid/gid defaults, initializes queues, and sets timeouts. Destruction cancels queued PDUs with callbacks, frees fragments/auth/fd/error queues/buffers, destroys locks, releases Kerberos data if enabled, and frees the context. Cursor functions maintain invariants while consuming or shrinking scatter/gather vectors.

## State And Persistence
State lives in `struct rpc_context`: queues, auth credentials, fd, timers, uid/gid, debug, error string, stats, fragments, Kerberos auth data, and service endpoints. Static `salt` diversifies XID seeds within the process. No filesystem persistence.

## Dependencies And Integration Points
Used by all libnfs client/server operations. Depends on raw RPC/NFS headers, auth creation, queue/list helpers, optional multithreading locks/atomics, optional Kerberos wrapper, and platform compatibility layers.

## Risks
PDU cancellation invokes callbacks while managing queues; callbacks must not assume entries still exist or enqueue unexpectedly. `rpc_set_hash_size` changes wait queues and should be used carefully under multithreading. Error strings are fixed 1024-byte buffers. Some setters rely on `assert(rpc->magic)` rather than runtime error returns.

## Test Signals
Test allocation failure paths, multithreaded error/stat access, hash resizing, destroy with queued out/wait PDUs, callback cancellation behavior, server context on blocking/nonblocking sockets, uid/gid auth replacement, Kerberos username cleanup, and cursor invariants under partial and full consumption.
