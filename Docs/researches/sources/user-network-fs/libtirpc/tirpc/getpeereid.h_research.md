# sources/user-network-fs/libtirpc/tirpc/getpeereid.h

Purpose: `getpeereid.h` declares `getpeereid`, the portability hook used to retrieve effective peer credentials from local sockets.

Important APIs, types, and functions: The only API is `int getpeereid(int s, uid_t *euid, gid_t *egid);`.

Control flow: This header has no control flow. Callers pass a socket descriptor and receive effective UID/GID outputs from the platform implementation.

State and persistence behavior: No state is declared or owned.

Dependencies and integration points: It integrates with `svc_vc.c` through `__rpc_get_local_uid`, which calls `getpeereid` for `AF_LOCAL` transports. The header assumes `uid_t` and `gid_t` are already available from included system/RPC headers.

Risks: Because this is only a prototype, portability depends on a matching implementation or system function being available at link time. Missing type includes can surface if included standalone before system type definitions.

Test signals: Build tests should include this header in the supported platform configurations, and AF_LOCAL service tests should validate peer UID extraction.
