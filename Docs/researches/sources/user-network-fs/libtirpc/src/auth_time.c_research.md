<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_time.c -->
# sources/user-network-fs/libtirpc/src/auth_time.c

Purpose: Private helper for AUTH_DES clock synchronization against rpcbind or inet time service.

Important APIs, types, and functions: Implements `__rpc_get_time_offset` plus helpers `alarm_hndler`, `uaddr_to_sockaddr`, `free_eps`, and `get_server`.

Control flow: If no cached universal address exists, it constructs/selects TCP or UDP endpoints. It converts universal addresses to IPv4 socket addresses, tries RPCBPROC_GETTIME over rpcbind, falls back to port 37 time service over UDP/TCP with timeout/alarm handling, then computes server-minus-client seconds and caches the universal address.

State and persistence behavior: Returns time delta in caller-provided `timeval`; may allocate and cache `*uaddr`. Temporarily changes SIGALRM handler and opens sockets/client handles.

Dependencies and integration points: Used by `auth_des.c` refresh. Depends on RPC client APIs, rpcbind protocol, sockets, NIS endpoint structures, and IPv4 universal address formatting.

Risks: IPv4-only parsing and string formatting limit transport support. The function changes process SIGALRM handling, which is risky in threaded programs. There is a likely rounding bug using `tv.tv_sec > 500000` instead of microseconds. Network time service fallback is legacy.

Test signals: No direct test; only AUTH_DES time sync users exercise it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_time.c -->
