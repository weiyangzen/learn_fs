# sources/user-network-fs/nfs-utils/support/nfs/svc_socket.c

Purpose: legacy helpers for creating nonblocking IPv4 RPC service sockets bound to service ports derived from RPC program numbers.

Important APIs: `getservport()`, `svcsock_nonblock()`, `svctcp_socket()`, and `svcudp_socket()`.

Control flow: `getservport()` maps an RPC program number to an RPC name/aliases and then to a TCP/UDP service port. `svc_socket()` creates AF_INET TCP/UDP sockets, optionally sets `SO_REUSEADDR`, binds to the service port, and marks the socket nonblocking. TCP and UDP wrappers choose socket type/protocol.

State and persistence: no global state; reads NSS databases for RPC/service entries and mutates socket state.

Dependencies and integration: used by legacy `rpcmisc.c`. Depends on `xlog`, `rpcmisc.h`, libc NSS, and socket APIs.

Risks: IPv4-only. If no service port is found, it binds port 0. Nonblocking conversion closes the socket on failure. Test-only `main()` is gated by `TEST`.

Test signals: known program-to-port mappings, aliases, missing service database entries, TCP reuse option, UDP no-reuse path, nonblocking flag, and bind failure.
